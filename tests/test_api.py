from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "videohosting-ml"}


def test_search_moments_mock():
    payload = {"query": "test query", "video_id": 42, "limit": 5}

    response = client.post("/api/v1/search/moments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
    assert data["results"][0]["video_id"] == 42
