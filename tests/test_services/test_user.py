import pytest

from unittest.mock import AsyncMock, patch

from app.entities.users.service import UserService

user_data = {
    "telegram_id": 12345,
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "balance": 0.0,
    "count_refer": 0,
}


@pytest.fixture
def mock_server_service():
    with patch("app.entities.users.service.ServerService") as mock:
        mock.find_one_or_none = AsyncMock()
        yield mock


@pytest.fixture
def mock_key_service():
    with patch("app.entities.users.service.KeyService") as mock:
        mock.generate_key = AsyncMock()
        mock.update_key = AsyncMock()
        mock.delete_key = AsyncMock()
        yield mock


@pytest.fixture
def mock_promocode_service():
    with patch("app.entities.users.service.PromocodeService") as mock:
        mock.find_one_or_none = AsyncMock()
        mock.update_count = AsyncMock()
        yield mock


@pytest.mark.asyncio
async def test_user():
    await UserService.add(**user_data)


# # @pytest.mark.asyncio
# # async def test_find_expiry_keys_no_keys():
# #     result = await UserService.find_expiry_keys(12345)
# #     assert result is None


# @pytest.mark.asyncio
# async def test_user_find():
#     result = await UserService.find_one_or_none(telegram_id=12345)
#     assert result is not None
#     assert result.telegram_id == 12345
#     assert result.username == "testuser"
#     assert result.balance == 0.0


# @pytest.mark.asyncio
# async def test_user_update_balance():
#     await UserService.update_balance(12345, 100)
#     result = await UserService.find_one_or_none(telegram_id=12345)
#     assert result.balance == 100  # type: ignore
#     await UserService.update_balance(12345, -100)


# @pytest.mark.asyncio
# async def test_update_balance_negative_amount():
#     await UserService.update_balance(12345, 100)
#     await UserService.update_balance(12345, -50.0)
#     user = await UserService.find_one_or_none(telegram_id=12345)
#     assert user.balance == 50.0  # type: ignore
#     await UserService.update_balance(12345, -50)


# @pytest.mark.asyncio
# async def test_update_balance_zero_amount():
#     await UserService.update_balance(12345, 100)
#     await UserService.update_balance(12345, 0.0)
#     user = await UserService.find_one_or_none(telegram_id=12345)
#     assert user.balance == 100.0  # type: ignore
#     await UserService.update_balance(12345, -100)


# @pytest.mark.asyncio
# async def test_update_balance_non_existent_user():
#     result = await UserService.update_balance(99999, 100.0)
#     assert result is None


# @pytest.mark.asyncio
# async def test_user_update_count_refer():
#     await UserService.update_count_refer(12345)
#     result = await UserService.find_one_or_none(telegram_id=12345)
#     assert result.count_refer == 1  # type: ignore


# @pytest.mark.asyncio
# async def test_update_count_refer_non_existent_user():
#     result = await UserService.update_count_refer(99999)
#     assert result is None


# @pytest.mark.asyncio
# async def test_user_update_balance_count_refer():
#     await UserService.update_balance_and_count_refer(12345, 100)
#     result = await UserService.find_one_or_none(telegram_id=12345)
#     assert result.count_refer == 2  # type: ignore
#     assert result.balance == 100  # type: ignore
#     await UserService.update_balance(12345, -100)


# @pytest.mark.asyncio
# async def test_update_balance_and_count_refer_negative_balance():
#     await UserService.update_balance_and_count_refer(12345, -50.0)
#     user = await UserService.find_one_or_none(telegram_id=12345)
#     assert user.balance == -50.0  # type: ignore
#     assert user.count_refer == 3  # type: ignore
#     await UserService.update_balance(12345, 50)


# @pytest.mark.asyncio
# async def test_update_balance_and_count_refer_non_existent_user():
#     result = await UserService.update_balance_and_count_refer(99999, 100.0)
#     assert result is None


# @pytest.mark.asyncio
# async def test_server():
#     async with async_session_maker() as session:
#         server = Server(id=1, name="test_server", domain="http://example.com")
#         session.add(server)
#         await session.commit()


# @pytest.mark.asyncio
# async def test_create_key_success(mock_server_service, mock_key_service):
#     mock_key = AsyncMock(
#         id="key123",
#         server_id=1,
#         value="key_value",
#         expiryTime="1234567890000",
#         email="test@example.com",
#     )
#     mock_key_service.generate_key.return_value = mock_key

#     await UserService.update_balance(12345, 150)
#     result = await UserService.create_key(12345, "test_server")
#     assert result is not None
#     user = await UserService.find_one_or_none(telegram_id=12345)
#     assert user.balance == 0.0  # type: ignore


# @pytest.mark.asyncio
# async def test_create_key_invalid_server(mock_server_service, mock_key_service):
#     mock_server_service.find_one_or_none.return_value = None
#     result = await UserService.create_key(12345, "invalid_server")
#     assert result is None


# @pytest.mark.asyncio
# async def test_create_key_insufficient_balance(mock_server_service, mock_key_service):
#     mock_key_service.generate_key.return_value = AsyncMock(
#         id="key123",
#         server_id=1,
#         value="key_value",
#         expiryTime="1234567890000",
#         email="test@example.com",
#     )

#     await UserService.update_balance(12345, 100)
#     result = await UserService.create_key(12345, "test_server")
#     assert result is not None
#     user = await UserService.find_one_or_none(telegram_id=12345)
#     assert user.balance == -50.0  # type: ignore


# @pytest.mark.asyncio
# async def test_create_key_failed_key_generation(mock_server_service, mock_key_service):
#     mock_key_service.generate_key.return_value = None
#     result = await UserService.create_key(12345, "test_server")
#     assert result is None


# @pytest.mark.asyncio
# async def test_update_key_success(mock_server_service, mock_key_service):
#     mock_key_service.update_key.return_value = True
#     data = KeyPayloadScheme(
#         id="key123",
#         email="test@example.com",
#         limitIp=3,
#         totalGb=107374182400,
#         expiryTime="1234567890000",
#     )
#     result = await UserService.update_key(
#         12345,
#         "test_server",
#         data,
#     )
#     assert result is True


# @pytest.mark.asyncio
# async def test_update_key_non_existent_user(mock_server_service, mock_key_service):
#     mock_key_service.update_key.return_value = True
#     data = KeyPayloadScheme(
#         id="key123",
#         email="test@example.com",
#         limitIp=3,
#         totalGb=107374182400,
#         expiryTime="1234567890000",
#     )
#     result = await UserService.update_key(
#         99999,
#         "test_server",
#         data,
#     )
#     assert result is False


# @pytest.mark.asyncio
# async def test_update_key_invalid_server(mock_server_service, mock_key_service):
#     mock_server_service.find_one_or_none.return_value = None
#     data = KeyPayloadScheme(
#         id="key123",
#         email="test@example.com",
#         limitIp=3,
#         totalGb=107374182400,
#         expiryTime="1234567890000",
#     )
#     result = await UserService.update_key(
#         12345,
#         "invalid_server",
#         data,
#     )
#     assert result is False


# @pytest.mark.asyncio
# async def test_delete_key_success(mock_server_service, mock_key_service):
#     mock_server_service.find_one_or_none.return_value = AsyncMock(
#         id=1,
#         name="test_server",
#     )
#     mock_key_service.delete_key.return_value = True
#     result = await UserService.delete_key(
#         12345,
#         "test_server",
#         "key123",
#     )
#     assert result is True


# @pytest.mark.asyncio
# async def test_delete_key_non_existent_user(mock_server_service, mock_key_service):
#     mock_key_service.delete_key.return_value = True
#     result = await UserService.delete_key(
#         99999,
#         "test_server",
#         "key123",
#     )
#     assert result is False


# @pytest.mark.asyncio
# async def test_delete_key_invalid_server(mock_server_service, mock_key_service):
#     mock_server_service.find_one_or_none.return_value = None
#     result = await UserService.delete_key(
#         12345,
#         "invalid_server",
#         "key123",
#     )
#     assert result is False


# @pytest.mark.asyncio
# async def test_get_all_keys_success(mock_server_service, mock_key_service):
#     mock_key_service.generate_key.return_value = AsyncMock(
#         id="key123",
#         server_id=1,
#         value="key_value",
#         expiryTime="1234567890000",
#         email="test@example.com",
#     )
#     await UserService.update_balance(12345, 150)
#     await UserService.create_key(12345, "test_server")
#     keys = await UserService.get_all_keys(12345)
#     assert len(keys) == 3  # type: ignore
#     assert keys[0].id_panel == "key123"  # type: ignore


# @pytest.mark.asyncio
# async def test_get_all_keys_non_existent_user():
#     result = await UserService.get_all_keys(99999)
#     assert result is None


# # @pytest.mark.asyncio
# # async def test_get_promocode_success(mock_promocode_service):
# #     promocode = AsyncMock(
# #         id=1,
# #         code="TEST123",
# #         bonus=50.0,
# #         count=1,
# #     )
# #     mock_promocode_service.find_one_or_none.return_value = promocode
# #     result = await UserService.get_promocode(12345, "TEST123")
# #     assert result is not None
# #     user = await UserService.find_one_or_none(telegram_id=12345)
# #     assert user.balance == 50.0  # type: ignore


# # @pytest.mark.asyncio
# # async def test_get_promocode_already_used(mock_promocode_service):
# #     promocode = AsyncMock(
# #         id=1,
# #         code="TEST123",
# #         bonus=50.0,
# #         count=1,
# #     )
# #     mock_promocode_service.find_one_or_none.return_value = 1
# #     user = await UserService.find_one_or_none(telegram_id=12345)
# #     user.promocodes_activate.append(promocode)  # type: ignore
# #     result = await UserService.get_promocode(12345, "TEST123")
# #     assert result is False


# # @pytest.mark.asyncio
# # async def test_get_promocode_zero_count(setup_user, mock_promocode_service):
# #     promocode = AsyncMock(
# #         id=1,
# #         code="TEST123",
# #         bonus=50.0,
# #         count=0,
# #     )
# #     mock_promocode_service.find_one_or_none.return_value = promocode
# #     result = await UserService.get_promocode(12345, "TEST123")
# #     assert result is None


# # @pytest.mark.asyncio
# # async def test_get_promocode_non_existent(setup_user, mock_promocode_service):
# #     mock_promocode_service.find_one_or_none.return_value = None
# #     result = await UserService.get_promocode(12345, "INVALID")
# #     assert result is None


# @pytest.mark.asyncio
# async def test_find_min_date_expire_no_keys():
#     result = await UserService.find_min_date_expire(12345)
#     assert result is None


# @pytest.mark.asyncio
# async def test_find_min_date_expire_single_key(mock_server_service, mock_key_service):
#     mock_server_service.find_one_or_none.return_value = AsyncMock(
#         id=1,
#         name="test_server",
#     )
#     mock_key_service.generate_key.return_value = AsyncMock(
#         id="key123",
#         server_id=1,
#         value="key_value",
#         expiryTime="1234567890000",
#         email="test@example.com",
#     )
#     await UserService.create_key(12345, "test_server")
#     result = await UserService.find_min_date_expire(12345)
#     expected_date = datetime.fromtimestamp(
#         1234567890000 / 1000, tz=timezone.utc
#     ).strftime("%Y-%m-%d")
#     assert result == expected_date


# # @pytest.mark.asyncio
# # async def test_find_min_date_expire_multiple_keys(
# #     mock_server_service, mock_key_service
# # ):
# #     mock_server_service.find_one_or_none.return_value = AsyncMock(
# #         id=1,
# #         name="test_server",
# #     )
# #     expiry1 = (datetime.now(timezone.utc) + timedelta(days=10)).timestamp() * 1000
# #     expiry2 = (datetime.now(timezone.utc) + timedelta(days=5)).timestamp() * 1000

# #     mock_key_service.generate_key.side_effect = [
# #         AsyncMock(
# #             id="key1",
# #             expiryTime=str(int(expiry1)),
# #         ),
# #         AsyncMock(
# #             id="key2",
# #             expiryTime=str(int(expiry2)),
# #         ),
# #     ]
# #     await UserService.update_balance(12345, 300)
# #     await UserService.create_key(12345, "test_server")
# #     await UserService.create_key(12345, "test_server")
# #     result = await UserService.find_min_date_expire(12345)
# #     expected_date = datetime.fromtimestamp(expiry2 / 1000, tz=timezone.utc).strftime(
# #         "%Y-%m-%d"
# #     )
# #     assert result == expected_date


# @pytest.mark.asyncio
# async def test_find_expiry_keys_no_expired_keys(mock_server_service, mock_key_service):
#     mock_server_service.find_one_or_none.return_value = AsyncMock(
#         id=1,
#         name="test_server",
#     )
#     mock_key_service.generate_key.return_value = AsyncMock(
#         id="key123",
#         server_id=1,
#         value="key_value",
#         expiryTime="1234567890000",
#         email="test@example.com",
#     )
#     await UserService.create_key(12345, "test_server")
#     result = await UserService.find_expiry_keys(12345)
#     assert result == []


# @pytest.mark.asyncio
# async def test_find_expiry_keys_with_expired_keys():
#     with patch.object(UserService, "get_all_keys", new=AsyncMock()) as mock_get_all:
#         key_expired = AsyncMock(status=False)
#         key_active = AsyncMock(status=True)
#         mock_get_all.return_value = [key_expired, key_active]
#         result = await UserService.find_expiry_keys(12345)
#         assert result == [key_expired]
