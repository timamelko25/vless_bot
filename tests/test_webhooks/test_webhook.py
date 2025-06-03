import time
import pytest

from fastapi.testclient import TestClient
from app.main import app


# Fixture for FastAPI test client
@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_webhook(client):
    # Mock an update payload (simplified for testing)
    update_payload = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "chat": {"id": 12345, "type": "private"},
            "date": int(time.time()),
            "text": "/start",
            "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
        },
    }

    response = client.post("/webhook", json=update_payload)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_healthcheck(client):
    response = client.get("/test")

    assert response.status_code == 200
