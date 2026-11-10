import json
from pathlib import Path

import numpy as np
import ollama
import pandas as pd
import umap
from pydantic import ValidationError
from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN

from src.api.schemas.comments import AudienceReport, AudienceReportLLM, TopicItem
from src.core.config import settings
from src.pipelines.clean_comments import clean_comments_pipeline

_model = None


def get_embedding_model() -> SentenceTransformer:
    """Lazy-load the SentenceTransformer model on first call to prevent slow imports."""
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model_name, device=settings.device)
    return _model


def analyse_sentiment_pipeline(
    df: pd.DataFrame,
    video_title: str,
    channel_name: str,
    target_language: str = "Ukrainian",
) -> AudienceReport:
    """
    Analyze sentiment of comments using UMAP, HDBSCAN, and LLM.
    """
    model = get_embedding_model()

    all_vectors = model.encode(
        df["text"].tolist(),
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    reducer = umap.UMAP(
        n_neighbors=15, n_components=5, metric="cosine", random_state=42
    )
    umap_vectors = reducer.fit_transform(all_vectors)

    min_cluster_size = max(5, min(20, int(len(df) * 0.05)))
    hdb = HDBSCAN(min_cluster_size=min_cluster_size, metric="cosine")
    df["hdb_cluster"] = hdb.fit_predict(umap_vectors)
    cluster_info = []
    valid_comments_count = len(df[df["hdb_cluster"] != -1])
    unique_clusters = sorted([c for c in df["hdb_cluster"].unique() if c != -1])
    if not unique_clusters:
        return AudienceReportLLM(
            executive_summary="Audience discussions are highly fragmented across various unrelated topics with no dominant consensus.",
            topics=[],
        )
    cluster_comment_ids = {}

    for c_id in unique_clusters:
        c_indices = df.index[df["hdb_cluster"] == c_id].to_numpy()
        c_vecs = all_vectors[c_indices]
        c_df = df.loc[c_indices].copy()
        cluster_comment_ids[c_id] = c_df["comment_id"].tolist()

        centroid = c_vecs.mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        c_df["sim_to_center"] = c_vecs @ centroid
        max_votes = c_df["votes"].max()
        vote_score = c_df["votes"] / max_votes if max_votes > 0 else 0
        c_df["rank_score"] = 0.7 * c_df["sim_to_center"] + 0.3 * vote_score

        top_examples = c_df.sort_values("rank_score", ascending=False).head(6)
        pct = round(len(c_df) / valid_comments_count * 100, 1)
        examples = "\n".join([f"  * {t.strip()[:250]}" for t in top_examples["text"]])
        cluster_info.append(
            f"Topic #{c_id} ({pct}% of comments, {len(c_df)} items):\n{examples}"
        )

    hdb_clusters_text = "\n\n".join(cluster_info)

    universal_prompt = f"""
    You are an expert video platform audience intelligence system.
    Analyze the following unsupervised comment clusters extracted from viewer reactions and produce an executive report for the creator.

    VIDEO CONTEXT:
    - Title: "{video_title}"
    - Channel: "{channel_name}"

    UNIVERSAL ATTRIBUTION & INTERPRETATION RULES:
    1. Clearly distinguish between the subjects of discussion:
    - Feedback regarding the Content Creator / Host (style, tone, presentation, video quality, questions).
    - Feedback regarding specific Guests, Interviewees, or Characters featured in the video.
    - General audience debates regarding the Topic itself (debates on history, facts, opinions).
    Criticism of a guest or topic is NOT criticism of the creator.
    2. Sentiment Nuance:
    - Shock, awe, or profound revelation (e.g. "this shocked me", "mind-blowing", "never thought of it") express positive intellectual appreciation, NOT negative criticism.
    - If comments within a single topic express divergent attitudes, mark sentiment as "mixed" and describe the divergence.
    3. Strict Grounding:
    - Base all topic titles and takeaways STRICTLY on the provided comments. Do not hallucinate, merge unrelated comments, or assume unmentioned facts.

    STYLE & LANGUAGE INTEGRITY:
    - Language: All generated text (executive_summary, titles, key_takeaways) MUST be strictly in {target_language}.
    - Syntactic Variety: Each topic takeaway must use a unique sentence structure and distinct vocabulary. Repetitive sentence starters and template phrasing across items are strictly prohibited.
    - Orthography: Adhere strictly to the standard grammar, vocabulary, and orthographic rules of {target_language}.

    AUDIENCE TOPIC CLUSTERS:
    {hdb_clusters_text}

    OUTPUT SCHEMA (STRICT JSON ONLY):
    {{
    "executive_summary": "One concise paragraph in {target_language} summarizing overall audience reception.",
    "topics": [
        {{
        "title": "Concise 3-5 word topic title in {target_language}",
        "sentiment": "positive" | "negative" | "mixed",
        "percentage": 0.0,
        "key_takeaway": "One clear, distinct sentence in {target_language} explaining what viewers are saying or feeling."
        }}
    ]
    }}
    """

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": universal_prompt}],
        format=AudienceReportLLM.model_json_schema(),
        options={"temperature": 0.3},
    )

    for attempt in range(2):
        try:
            llm_report = AudienceReportLLM.model_validate_json(
                response["message"]["content"]
            )

            enriched_topics = []
            for i, topic in enumerate(llm_report.topics):
                c_id = unique_clusters[i] if i < len(unique_clusters) else None
                c_ids = cluster_comment_ids.get(c_id, []) if c_id is not None else []

                enriched_topics.append(
                    TopicItem(
                        **topic.model_dump(),
                        comment_ids=c_ids,
                    )
                )

            return AudienceReport(
                executive_summary=llm_report.executive_summary,
                topics=enriched_topics,
            )
        except ValidationError as e:
            if attempt == 1:
                print(f"Validation failed after 2 attempts: {e}")
                raise

            print(f"Validation failed, retrying... Attempt {attempt + 1}")

            repair_message = (
                f"Your previous response failed validation with error:\n{e}\n"
                f"Please fix the output to strictly match the schema."
            )

            response = ollama.chat(
                model="llama3.1:8b",
                messages=[
                    {"role": "user", "content": universal_prompt},
                    {
                        "role": "assistant",
                        "content": response["message"]["content"],
                    },
                    {"role": "user", "content": repair_message},
                ],
                format=AudienceReportLLM.model_json_schema(),
                options={"temperature": 0.3},
            )


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    csv_path = project_root / "data" / "raw" / "youtube_comments_1000.csv"
    meta_path = csv_path.with_suffix(".meta.json")
    df = pd.read_csv(csv_path, encoding="utf-8")
    df = clean_comments_pipeline(df)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    video_title = meta["title"]
    channel_name = meta["channel"]
    target_language = "Ukrainian"

    report = analyse_sentiment_pipeline(
        df=df,
        video_title=video_title,
        channel_name=channel_name,
        target_language=target_language,
    )

    print(report.model_dump_json(indent=2))
