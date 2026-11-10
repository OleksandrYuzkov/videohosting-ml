import uuid

import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

from src.core.config import settings
from src.core.embeddings import compute_sparse_vector
from src.core.qdrant import get_qdrant_client, init_collection
from src.pipelines.clean_comments import clean_comments_pipeline


def index_comments_pipeline(
    df: pd.DataFrame,
    video_id: str,
    client: QdrantClient | None = None,
    batch_size: int = 64,
) -> None:

    if client is None:
        client = get_qdrant_client()
    init_collection(client)
    model = SentenceTransformer(settings.embedding_model_name, device=settings.device)

    passaages = [f"passage: {text}" for text in df["text"]]
    dense_vectors = model.encode(passaages, batch_size=batch_size, show_progress_bar=True)

    points = []
    for idx, (_, row) in enumerate(df.iterrows()):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(row.get("cid", idx))))
        text = str(row.get("text", ""))
        vector ={
            'dense': dense_vectors[idx].tolist(),
            'sparse': compute_sparse_vector(text),
        }
        payload = {
            "video_id": video_id,
            "cid": str(row.get("cid", idx)),
            "author": str(row.get("author", "unknown")),
            "text": str(row.get("text", "")),
            "votes": int(row.get("votes", 0)),
        }
        points.append(models.PointStruct(id=point_id, vector=vector, payload=payload))

    client.upsert(collection_name="comments_hybrid", points=points)

if __name__ == "__main__":
    df = pd.read_csv("data/raw/youtube_comments_1000.csv")
    df = clean_comments_pipeline(df)

    print(f"Indexing {len(df)} comments into Qdrant...")
    index_comments_pipeline(df, video_id="example_video_id")
    print("Done! Refresh your Qdrant collection to see the indexed comments.")