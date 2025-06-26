from fastapi.testclient import TestClient

from backend.api.main import app


def test_me_endpoint_returns_anonymous():
    client = TestClient(app)
    response = client.get("/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "anonymous@example.com"
    assert data["role"] == "anonymous"
