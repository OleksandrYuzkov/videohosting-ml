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


def test_analyze_comments_insufficient_data():
    """Test that the endpoint returns HTTP 400 when fewer than 15 comments are provided."""
    payload = {
        "video_id": 1,
        "video_title": "Test Video",
        "channel_name": "Test Channel",
        "target_language": "English",
        "comments": [
            {"comment_id": 1, "text": "First comment", "votes": 5},
            {"comment_id": 2, "text": "Second comment", "votes": 2},
        ],
    }
    response = client.post("/api/v1/comments/analyze", json=payload)
    # Verify HTTP 400 Bad Request and error detail message
    assert response.status_code == 400
    assert "Insufficient comments" in response.json()["detail"]
