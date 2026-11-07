from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.core.config import settings


def get_qdrant_client() -> QdrantClient:
    """
    Creates a Qdrant client based on configuration.
    Connects to Qdrant Cloud if credentials exist, otherwise falls back to local
    disk storage.
    """
    if settings.qdrant_url and settings.qdrant_api_key:
        return QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

    return QdrantClient(path="./data/qdrant_storage")


def init_collection(
    client: QdrantClient,
    collection_name: str = "comments",
    vector_size: int = settings.embedding_dim,
) -> None:
    """Initializes a collection in Qdrant if it doesn't already exist."""
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size, distance=models.Distance.COSINE
            ),
        )
