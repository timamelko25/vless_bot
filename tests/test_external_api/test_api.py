import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientError
from app.external_api import panel_api
from app.entities.keys.schemas import KeyPayloadScheme

URL = "https://example.com"

@pytest.mark.asyncio
async def test_open_session_success():
    cookies = {"cookies": "test_cookie"}

    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 200
    mock_response.__aenter__.return_value.cookies = cookies

    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        session, result_cookies = await panel_api.open_session(URL + "/")
        assert result_cookies == cookies
        await session.close()

@pytest.mark.asyncio
async def test_open_session_failure():
    with patch("aiohttp.ClientSession.post", side_effect=ClientError("connection failed")):
        session, cookies = await panel_api.open_session(URL + "/")
        assert cookies is None
        assert session is None

@pytest.mark.asyncio
async def test_get_inbounds_success():
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 200
    mock_response.__aenter__.return_value.json = AsyncMock(return_value={"key": "value"})

    session = MagicMock()
    session.get.return_value = mock_response

    result = await panel_api.get_inbounds(session, {"cookies": "test"}, URL + "/")
    assert result == {"key": "value"}

@pytest.mark.asyncio
async def test_get_inbounds_failure_status():
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 500
    mock_response.__aenter__.return_value.json = AsyncMock(return_value={"error": "server error"})

    session = MagicMock()
    session.get.return_value = mock_response

    result = await panel_api.get_inbounds(session, {"cookies": "test"}, URL + "/")
    assert result == {}

@pytest.mark.asyncio
async def test_add_client_success():
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 200
    mock_response.__aenter__.return_value.json = AsyncMock(return_value={"success": True})

    session = MagicMock()
    session.post.return_value = mock_response

    key_data = KeyPayloadScheme(
        id="abc123",
        email="user@example.com",
        limitIp=1,
        totalGb=10,
        expiryTime="2025-12-31T23:59:59",
        status=True,
    )

    result = await panel_api.add_client(session, {"cookies": "test"}, URL + "/", key_data)
    assert result == {"success": True}

@pytest.mark.asyncio
async def test_add_client_failure_status():
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 400
    mock_response.__aenter__.return_value.json = AsyncMock(return_value={"error": "bad request"})

    session = MagicMock()
    session.post.return_value = mock_response

    key_data = KeyPayloadScheme(
        id="abc123",
        email="user@example.com",
        limitIp=1,
        totalGb=10,
        expiryTime="2025-12-31T23:59:59",
        status=True,
    )

    result = await panel_api.add_client(session, {"cookies": "test"}, URL + "/", key_data)
    assert result == {}

@pytest.mark.asyncio
async def test_update_client_success():
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 200
    mock_response.__aenter__.return_value.json = AsyncMock(return_value={"updated": True})

    session = MagicMock()
    session.post.return_value = mock_response

    key_data = KeyPayloadScheme(
        id="abc123",
        email="user@example.com",
        limitIp=1,
        totalGb=10,
        expiryTime="2025-12-31T23:59:59",
        status=True,
    )

    result = await panel_api.update_client(session, {"cookies": "test"}, URL + "/", "abc123", key_data)
    assert result == {"updated": True}

@pytest.mark.asyncio
async def test_update_client_failure_status():
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 404
    mock_response.__aenter__.return_value.json = AsyncMock(return_value={"error": "not found"})

    session = MagicMock()
    session.post.return_value = mock_response

    key_data = KeyPayloadScheme(
        id="abc123",
        email="user@example.com",
        limitIp=1,
        totalGb=10,
        expiryTime="2025-12-31T23:59:59",
        status=True,
    )

    result = await panel_api.update_client(session, {"cookies": "test"}, URL + "/", "abc123", key_data)
    assert result == {}

@pytest.mark.asyncio
async def test_delete_client_success():
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 200
    mock_response.__aenter__.return_value.json = AsyncMock(return_value={"deleted": True})

    session = MagicMock()
    session.post.return_value = mock_response

    result = await panel_api.delete_client(session, {"cookies": "test"}, URL + "/", "1", "abc123")
    assert result == {"deleted": True}

@pytest.mark.asyncio
async def test_delete_client_failure():
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value.status = 403
    mock_response.__aenter__.return_value.json = AsyncMock(return_value={"error": "forbidden"})

    session = MagicMock()
    session.post.return_value = mock_response

    result = await panel_api.delete_client(session, {"cookies": "test"}, URL + "/", "1", "abc123")
    assert result == {}
