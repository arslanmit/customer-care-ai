from fastapi.testclient import TestClient

from backend.api.main import _create_jwt, app


def test_me_endpoint_requires_auth():
    client = TestClient(app)
    response = client.get("/me")
    assert response.status_code == 401


def test_me_endpoint_returns_claims():
    client = TestClient(app)
    token = _create_jwt({"id": "123", "email": "u@example.com", "role": "user"})
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "u@example.com"
