import uuid

import pandas as pd
import torch
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

from src.core.config import settings
from src.core.qdrant import get_qdrant_client, init_collection


def index_comments_pipeline(
    df: pd.DataFrame,
    video_id: str,
    client: QdrantClient | None = None,
    batch_size: int = 64,
) -> None:

    if client is None:
        client = get_qdrant_client()
    init_collection(client)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(settings.embedding_model_name, device=device)

    passaages = [f"passage: {text}" for text in df["text"]]
    vectors = model.encode(passaages, batch_size=batch_size, show_progress_bar=True)

    points = []
    for idx, (_, row) in enumerate(df.iterrows()):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(row.get("cid", idx))))
        vector = vectors[idx].tolist()
        payload = {
            "video_id": video_id,
            "cid": str(row.get("cid", idx)),
            "author": str(row.get("author", "unknown")),
            "text": str(row.get("text", "")),
            "votes": int(row.get("votes", 0)),
        }
        points.append(models.PointStruct(id=point_id, vector=vector, payload=payload))

    client.upsert(collection_name="comments", points=points)
