import time
import pytest

from httpx import AsyncClient, ASGITransport
from app.main import app


# Fixture for FastAPI test client
@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


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

    response = await client.post("/webhook", json=update_payload)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_healthcheck(client):
    response = await client.get("/test")

    assert response.status_code == 200
