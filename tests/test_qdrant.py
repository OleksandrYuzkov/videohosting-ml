from qdrant_client import QdrantClient

from src.core.qdrant import get_qdrant_client, init_collection


def test_qdrant_connection():
    client = get_qdrant_client()
    assert isinstance(client, QdrantClient)

    init_collection(client, collection_name="test_collection")

    assert client.collection_exists("test_collection")
