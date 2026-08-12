from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_event_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_publish_event():
    response = client.post(
        "/events",
        json={
            "type": "service.created",
            "source": "platform-api",
            "subject": "payments-api",
            "data": {
                "owner": "payments-team"
            }
        }
    )

    assert response.status_code == 201
    assert response.json()["type"] == "service.created"
    assert response.json()["source"] == "platform-api"
    assert response.json()["id"]


def test_list_events():
    response = client.get("/events")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
