from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoint_returns_expected_shape():
    response = client.post("/chat", json={"session_id": "s1", "message": "why is my bill high"})
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"answer", "sources", "escalated", "intent"}
    assert body["intent"] == "billing"


def test_chat_endpoint_escalates_mutating_request():
    response = client.post(
        "/chat", json={"session_id": "s1", "message": "please issue a refund immediately"}
    )
    assert response.status_code == 200
    assert response.json()["escalated"] is True


def test_chat_endpoint_rejects_malformed_request():
    response = client.post("/chat", json={"session_id": "s1"})  # missing 'message'
    assert response.status_code == 422
