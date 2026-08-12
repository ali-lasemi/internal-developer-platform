import os

os.environ["DATABASE_URL"] = "sqlite:///./test_catalog.db"

from fastapi.testclient import TestClient

from app.db.database import Base
from app.db.database import engine
from app.main import app


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_catalog_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_service():
    response = client.post(
        "/catalog",
        json={
            "name": "example-service",
            "owner": "platform-team",
            "repository": "https://github.com/example/example-service",
            "description": "Example managed service",
            "lifecycle": "created"
        }
    )

    assert response.status_code == 201
    assert response.json()["name"] == "example-service"
    assert response.json()["id"] >= 1


def test_duplicate_service_is_rejected():
    response = client.post(
        "/catalog",
        json={
            "name": "example-service",
            "owner": "platform-team",
            "repository": "https://github.com/example/example-service",
            "description": "Duplicate service",
            "lifecycle": "created"
        }
    )

    assert response.status_code == 409


def test_list_catalog():
    response = client.get("/catalog")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_service():
    created = client.post(
        "/catalog",
        json={
            "name": "payments-api",
            "owner": "payments-team",
            "repository": "https://github.com/example/payments-api",
            "description": "Payments API",
            "lifecycle": "development"
        }
    )

    service_id = created.json()["id"]

    response = client.get(
        f"/catalog/{service_id}"
    )

    assert response.status_code == 200
    assert response.json()["name"] == "payments-api"
