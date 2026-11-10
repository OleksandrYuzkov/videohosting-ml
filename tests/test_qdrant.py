from qdrant_client import QdrantClient

from src.core.qdrant import init_collection


def test_qdrant_connection():
    client = QdrantClient(":memory:")
    assert isinstance(client, QdrantClient)

    init_collection(client, collection_name="test_collection")

    assert client.collection_exists("test_collection")
