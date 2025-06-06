import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.entities.keys.service import KeyService
from app.entities.keys.schemas import (
    KeyPayloadScheme,
    KeyScheme,
    PanelResponse,
    generate_vless_key,
)
from app.entities.servers.models import Server
from app.entities.users.models import User
from app.database import async_session_maker

# Sample data for testing
server_data = Server(
    id=1,
    name="test_server",
    domain="https://example.com:443",
)

key_payload_data = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "test@example.com",
    "limitIp": 2,
    "totalGb": 1000,
    "expiryTime": "2025-12-31T23:59:59",
    "status": True,
}

panel_response_data = {
    "success": True,
    "msg": "Success",
    "obj": [
        {
            "id": 1,
            "up": 0,
            "down": 0,
            "total": 0,
            "remark": "test",
            "enable": True,
            "expiryTime": 0,
            "clientStats": [],
            "port": 443,
            "protocol": "vless",
            "streamSettings": {
                "network": "tcp",
                "security": "reality",
                "realitySettings": {
                    "show": False,
                    "xver": 0,
                    "dest": "example.com:443",
                    "serverNames": ["example.com"],
                    "privateKey": "private_key",
                    "minClient": "",
                    "maxClient": "",
                    "maxTimediff": 0,
                    "shortIds": ["short_id"],
                    "settings": {
                        "publicKey": "public_public_key",
                        "fingerprint": "chrome",
                        "serverName": "example.com",
                        "spiderX": "",
                    },
                },
            },
        }
    ],
}

user = User(
    id=1,
    telegram_id=1,
    )

key_data = {
    "id": 1,
    "user_id": user.id,
    "server_id": server_data.id,
    "id_panel": "123-456",
    "email": "test@example.com",
    "value": "test_value",
    "expires_at": "2025-12-31T23:59:59",
    "status": True,
}

@pytest.mark.asyncio
async def test_data():
    async with async_session_maker() as session:
        session.add(user)
        session.add(server_data)
        await session.commit()


@pytest.fixture
def mock_panel_api():
    # Explicitly create AsyncMock objects for each function
    mock_open_session = AsyncMock(
        return_value=(
            AsyncMock(),
            {"cookies": "test_cookies"},
        ),
    )

    mock_get_inbounds = AsyncMock(return_value=panel_response_data)
    mock_add_client = AsyncMock(return_value=None)
    mock_delete_client = AsyncMock(return_value=None)
    mock_update_client = AsyncMock(return_value=None)

    with (
        patch("app.entities.keys.service.open_session", mock_open_session),
        patch("app.entities.keys.service.get_inbounds", mock_get_inbounds),
        patch("app.entities.keys.service.add_client", mock_add_client),
        patch("app.entities.keys.service.delete_client", mock_delete_client),
        patch("app.entities.keys.service.update_client", mock_update_client),
    ):
        yield {
            "open_session": mock_open_session,
            "get_inbounds": mock_get_inbounds,
            "add_client": mock_add_client,
            "delete_client": mock_delete_client,
            "update_client": mock_update_client,
        }


@pytest.mark.asyncio
async def test_find_all_keys_empty():
    # Test retrieving all keys when none exist
    result = await KeyService.find_all()
    assert result == []

@pytest.mark.asyncio
async def test_generate_key_success(mock_panel_api):
    # Test successful key generation
    data = KeyPayloadScheme(**key_payload_data)
    result = await KeyService.generate_key(data, server_data)

    assert isinstance(result, KeyScheme)
    assert result.id == "123e4567-e89b-12d3-a456-426614174000"
    assert result.email == "test@example.com"
    assert result.limitIp == 2
    assert result.totalGb == 1000
    assert result.expiryTime == "2025-12-31T23:59:59"
    assert result.status is True
    assert result.server_id == 1
    assert result.value == (
        f"vless://{data.id}@example.com:443?"
        "type=tcp&security=reality&pbk=public_public_key&fp=chrome"
        "&sni=example.com&sid=short_id&spx=%2F&flow=xtls-rprx-vision#test@example.com"
    )


@pytest.mark.asyncio
async def test_generate_key_session_failure(mock_panel_api):
    # Test session establishment failure
    mock_panel_api["open_session"].return_value = (None, None)
    data = KeyPayloadScheme(**key_payload_data)
    with pytest.raises(RuntimeError, match="Session not established"):
        await KeyService.generate_key(data, server_data)
    mock_panel_api["get_inbounds"].assert_not_awaited()
    mock_panel_api["add_client"].assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_key_api_error(mock_panel_api):
    # Test external API error during get_inbounds
    mock_panel_api["get_inbounds"].side_effect = Exception("API error")
    data = KeyPayloadScheme(**key_payload_data)
    with pytest.raises(Exception, match="API error"):
        await KeyService.generate_key(data, server_data)
    mock_panel_api["open_session"].assert_awaited_once()
    mock_panel_api["get_inbounds"].assert_awaited_once()
    mock_panel_api["add_client"].assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_key_invalid_panel_response(mock_panel_api):
    # Test malformed PanelResponse data
    invalid_panel_data = {
        "success": True,
        "msg": "Success",
        "obj": [],
    }  # Empty obj
    mock_panel_api["get_inbounds"].return_value = invalid_panel_data
    data = KeyPayloadScheme(**key_payload_data)
    with pytest.raises(IndexError):  # Accessing panel.obj[0] will fail
        await KeyService.generate_key(data, server_data)
    mock_panel_api["open_session"].assert_awaited_once()
    mock_panel_api["get_inbounds"].assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_key_database_error(mock_panel_api):
    # Test database error during key creation
    with patch(
        "app.entities.keys.models.Key.__init__",
        side_effect=SQLAlchemyError("Add failed"),
    ):
        data = KeyPayloadScheme(**key_payload_data)
        with pytest.raises(SQLAlchemyError):
            await KeyService.add(
                **data.model_dump(), value="vless://test-key", server_id=1
            )
    mock_panel_api["open_session"].assert_not_awaited()



@pytest.mark.asyncio
async def test_update_key_session_failure(mock_panel_api):
    # Test session establishment failure during update
    mock_panel_api["open_session"].return_value = (None, None)
    data = KeyPayloadScheme(**key_payload_data)
    with pytest.raises(RuntimeError, match="Session not established"):
        await KeyService.update_key(data, server_data)
    mock_panel_api["update_client"].assert_not_awaited()


@pytest.mark.asyncio
async def test_update_key_api_error(mock_panel_api):
    # Test external API error during update
    mock_panel_api["update_client"].side_effect = Exception("API error")

    data = KeyPayloadScheme(**key_payload_data)
    data2 = key_data
    data2["id"] = 2
    await KeyService.add(
        **data2,
    )

    result = await KeyService.update_key(data, server_data)

    assert result == {}  # Empty dict on error
    mock_panel_api["open_session"].assert_awaited_once()
    mock_panel_api["update_client"].assert_awaited_once()


@pytest.mark.asyncio
async def test_update_key_not_found(mock_panel_api):
    # Test updating non-existent key
    data = KeyPayloadScheme(**key_payload_data)

    result = await KeyService.update_key(data, server_data)

    assert result == 0  # Empty dict since no DB update occurs

    mock_panel_api["open_session"].assert_awaited_once()
    mock_panel_api["update_client"].assert_awaited_once()


# @pytest.mark.asyncio
# async def test_delete_key_success(mock_panel_api):
#     # Test successful key deletion
#     data = KeyPayloadScheme(**key_payload_data)
#     data2 = key_data
#     data2["id"] = 3
#     await KeyService.add(**data2)

#     result = await KeyService.delete_key(
#         uuid="123e4567-e89b-12d3-a456-426614174000", server=server_data, inboundId="1"
#     )

#     assert result is True
#     mock_panel_api["open_session"].assert_awaited_once_with(
#         url="https://example.com:443"
#     )
#     mock_panel_api["delete_client"].assert_awaited_once_with(
#         session=mock_panel_api["open_session"].return_value[0],
#         cookies=mock_panel_api["open_session"].return_value[1],
#         url="https://example.com:443",
#         inboundId="1",
#         uuid="123e4567-e89b-12d3-a456-426614174000",
#     )
#     deleted_key = await KeyService.find_one_or_none(
#         id_panel="123e4567-e89b-12d3-a456-426614174000"
#     )
#     assert deleted_key is None


@pytest.mark.asyncio
async def test_delete_key_session_failure(mock_panel_api):
    # Test session establishment failure during deletion
    mock_panel_api["open_session"].return_value = (None, None)
    with pytest.raises(RuntimeError, match="Session not established"):
        await KeyService.delete_key(
            uuid="123e4567-e89b-12d3-a456-426614174000",
            server=server_data,
            inboundId="1",
        )
    mock_panel_api["delete_client"].assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_key_api_error(mock_panel_api):
    # Test external API error during deletion
    mock_panel_api["delete_client"].side_effect = Exception("API error")
    data = key_data
    data["id"] = 4
    data["id_panel"] = "123-789"
    await KeyService.add(**data)
    result = await KeyService.delete_key(
        uuid="123-789", server=server_data, inboundId="1"
    )
    assert result is False
    mock_panel_api["open_session"].assert_awaited_once()
    mock_panel_api["delete_client"].assert_awaited_once()


# @pytest.mark.asyncio
# async def test_delete_key_not_found(mock_panel_api):
#     # Test deleting non-existent key
#     # Mock delete_client to raise an exception to simulate key not found in panel
#     mock_panel_api["delete_client"].side_effect = Exception("Client not found")
#     result = await KeyService.delete_key(
#         uuid="non-existent-uuid",
#         server=server_data,
#         inboundId="1",
#     )
#     assert result is False
#     mock_panel_api["open_session"].assert_awaited_once_with(
#         url="https://example.com:443"
#     )
#     mock_panel_api["delete_client"].assert_awaited_once_with(
#         session=mock_panel_api["open_session"].return_value[0],
#         cookies=mock_panel_api["open_session"].return_value[1],
#         url="https://example.com:443",
#         inboundId="1",
#         uuid="non-existent-uuid",
#     )
#     # Verify no key exists in database
#     key = await KeyService.find_one_or_none(id_panel="non-existent-uuid")
#     assert key is None



# @pytest.mark.asyncio
# async def test_find_all_keys_with_data():
#     # Test retrieving all keys with existing data
#     data1 = key_data
#     data1["id"] = 5
#     data2 = key_data
#     data2["id"] = 17
#     data2["id_panel"] = "456-789"
    
#     await KeyService.add(**data1)
#     await KeyService.add(**data2)
#     result = await KeyService.find_all()
#     assert isinstance(result, list)
#     assert any(key.id_panel == "123-456" for key in result)
#     assert any(key.id_panel == "456-789" for key in result)
    
    
# @pytest.mark.asyncio
# async def test_update_key_success(mock_panel_api):
#     # Test successful key update
#     data = key_data
#     data["id"] = 7
#     payload = KeyPayloadScheme(**key_payload_data)

#     await KeyService.add(**data)

#     result = await KeyService.update_key(payload, server_data)
#     assert result == 1  # 1 row affected

#     mock_panel_api["open_session"].assert_awaited_once_with(
#         url="https://example.com:443"
#     )

#     mock_panel_api["update_client"].assert_awaited_once_with(
#         session=mock_panel_api["open_session"].return_value[0],
#         cookies=mock_panel_api["open_session"].return_value[1],
#         url="https://example.com:443",
#         data=payload,
#         uuid=payload.id,
#     )
#     updated_key = await KeyService.find_one_or_none(
#         id_panel="123e4567-e89b-12d3-a456-426614174000"
#     )

#     assert updated_key.status is True
#     assert updated_key.expires_at == "2025-12-31T23:59:59"


@pytest.mark.asyncio
async def test_find_all_keys_error():
    # Test database error during find_all
    with patch(
        "app.entities.keys.service.KeyService.find_all",
        side_effect=SQLAlchemyError("Find all failed"),
    ):
        with pytest.raises(SQLAlchemyError):
            await KeyService.find_all()


@pytest.mark.asyncio
async def test_generate_vless_key():
    # Test generate_vless_key function
    data = KeyPayloadScheme(**key_payload_data)
    panel = PanelResponse(**panel_response_data)
    result = generate_vless_key(data, panel, "example.com")
    assert result == (
        f"vless://{data.id}@example.com:443?"
        "type=tcp&security=reality&pbk=public_public_key&fp=chrome"
        "&sni=example.com&sid=short_id&spx=%2F&flow=xtls-rprx-vision#test@example.com"
    )


@pytest.mark.asyncio
async def test_generate_vless_key_empty_panel_response():
    # Test generate_vless_key with empty panel response
    data = KeyPayloadScheme(**key_payload_data)
    invalid_panel = PanelResponse(success=True, msg="Success", obj=[])
    with pytest.raises(IndexError):
        generate_vless_key(data, invalid_panel, "example.com")
