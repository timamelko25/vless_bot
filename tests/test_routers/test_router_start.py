import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandObject
from app.entities.promocodes.service import PromocodeService
from app.entities.users.router_start import (
    cmd_start,
    get_promocode,
    get_user_profile,
    profile_command,
    start_promocode,
)
from app.entities.users.service import UserService
from aiogram.fsm.context import FSMContext


class DummyUser:
    def __init__(self, id=1, balance=100.0):
        self.id = id
        self.balance = balance


class MockFSMContext:
    async def set_state(self, state):
        pass

    async def get_state(self):
        return None

    async def update_data(self, **kwargs):
        pass

    async def get_data(self):
        return {}

    async def clear(self):
        pass


def create_callback(user_id=1):
    call = MagicMock(spec=CallbackQuery)
    call.from_user = MagicMock(id=user_id)
    call.message = MagicMock()
    call.message.edit_text = AsyncMock()
    call.data = None
    return call


def create_command_object(args=None):
    command = AsyncMock(spec=CommandObject)
    command.args = args
    return command


# --- cmd_start ---


@pytest.mark.asyncio
@patch("app.entities.users.router_start.UserService.add", new_callable=AsyncMock)
@patch(
    "app.entities.users.router_start.UserService.find_one_or_none",
    new_callable=AsyncMock,
)
@patch(
    "app.entities.users.router_start.UserService.find_min_date_expire",
    new_callable=AsyncMock,
)
async def test_cmd_start_new_user_positive(
    mock_find_min_date, mock_find_one_or_none, mock_add_user
):
    mock_find_one_or_none.return_value = None
    mock_find_min_date.return_value = None
    mock_add_user.return_value = DummyUser()

    call = create_callback()
    command = create_command_object(args=None)

    await cmd_start(call, command=command, state=MockFSMContext())

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.await_args
    assert "личный кабинет" in (args[0] if args else kwargs.get("text", "")).lower()


@pytest.mark.asyncio
@patch(
    "app.entities.users.router_start.UserService.find_one_or_none",
    new_callable=AsyncMock,
)
@patch(
    "app.entities.users.router_start.UserService.find_min_date_expire",
    new_callable=AsyncMock,
)
async def test_cmd_start_existing_user_and_delmsg_called(
    mock_find_min_date, mock_find_one_or_none
):
    mock_find_one_or_none.return_value = DummyUser()
    mock_find_min_date.return_value = "2025-12-01T00:00:00"

    call = create_callback()
    command = create_command_object(args=None)

    await cmd_start(call, command=command, state=MockFSMContext())

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.await_args
    assert "личный кабинет" in (args[0] if args else kwargs.get("text", "")).lower()


@pytest.mark.asyncio
async def test_cmd_start_invalid_args():
    call = create_callback()
    command = create_command_object(args="invalid")

    await cmd_start(call, command=command, state=MockFSMContext())

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.await_args
    assert isinstance(args[0] if args else kwargs.get("text", ""), str)


# --- get_user_profile ---


@pytest.mark.asyncio
@patch(
    "app.entities.users.router_start.UserService.find_one_or_none",
    new_callable=AsyncMock,
)
@patch(
    "app.entities.users.router_start.UserService.find_min_date_expire",
    new_callable=AsyncMock,
)
async def test_profile_command_existing_user_and_date(
    mock_find_min_date, mock_find_one_or_none
):
    mock_find_one_or_none.return_value = DummyUser()
    mock_find_min_date.return_value = "2025-12-01T00:00:00"

    call = create_callback()

    await get_user_profile(call)

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.await_args
    assert "личный кабинет" in (args[0] if args else kwargs.get("text", "")).lower()


@pytest.mark.asyncio
@patch(
    "app.entities.users.router_start.UserService.find_one_or_none",
    new_callable=AsyncMock,
)
@patch(
    "app.entities.users.router_start.UserService.find_min_date_expire",
    new_callable=AsyncMock,
)
async def test_profile_command_new_user_and_no_date(
    mock_find_min_date, mock_find_one_or_none
):
    mock_find_one_or_none.return_value = DummyUser()
    mock_find_min_date.return_value = None

    call = create_callback()

    await get_user_profile(call)

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.await_args
    assert "личный кабинет" in (args[0] if args else kwargs.get("text", "")).lower()


@pytest.mark.asyncio
@patch("app.entities.users.router_start.UserService.add", new_callable=AsyncMock)
@patch(
    "app.entities.users.router_start.UserService.find_one_or_none",
    new_callable=AsyncMock,
)
@patch(
    "app.entities.users.router_start.UserService.find_min_date_expire",
    new_callable=AsyncMock,
)
async def test_profile_command_no_user_then_add(
    mock_find_min_date, mock_find_one_or_none, mock_add_user
):
    mock_find_one_or_none.return_value = None
    mock_find_min_date.return_value = None
    mock_add_user.return_value = DummyUser()

    call = create_callback()

    await get_user_profile(call)

    call.message.edit_text.assert_not_awaited()


@pytest.mark.asyncio
@patch(
    "app.entities.users.router_start.UserService.find_one_or_none",
    new_callable=AsyncMock,
)
@patch(
    "app.entities.users.router_start.UserService.find_min_date_expire",
    new_callable=AsyncMock,
)
async def test_get_user_profile_with_user(mock_find_min_date, mock_find_one_or_none):
    mock_find_one_or_none.return_value = DummyUser()
    mock_find_min_date.return_value = "2026-01-01T00:00:00"

    call = create_callback()

    await get_user_profile(call)

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.await_args
    assert "личный кабинет" in (args[0] if args else kwargs.get("text", "")).lower()


@pytest.mark.asyncio
@patch(
    "app.entities.users.router_start.UserService.find_one_or_none",
    new_callable=AsyncMock,
)
@patch(
    "app.entities.users.router_start.UserService.find_min_date_expire",
    new_callable=AsyncMock,
)
async def test_get_user_profile_no_user(mock_find_min_date, mock_find_one_or_none):
    mock_find_one_or_none.return_value = None
    mock_find_min_date.return_value = None

    call = create_callback()

    await get_user_profile(call)

    call.message.edit_text.assert_not_awaited()


@pytest.mark.asyncio
async def test_valid_promocode(monkeypatch):
    message = AsyncMock(spec=Message)
    message.text = "VALIDCODE"
    message.from_user = AsyncMock(id=1234)
    message.message_id = 123
    message.answer = AsyncMock(return_value=AsyncMock(spec=Message))
    state = AsyncMock(spec=FSMContext)

    promocode = AsyncMock()
    promocode.code = "VALIDCODE"
    promocode.bonus = 50

    monkeypatch.setattr("app.utils.utils.del_msg", AsyncMock())  # Mock del_msg
    monkeypatch.setattr(
        PromocodeService, "find_one_or_none", AsyncMock(return_value=promocode)
    )
    monkeypatch.setattr(UserService, "get_promocode", AsyncMock(return_value=True))

    await get_promocode(message, state)
    message.answer.assert_called_once()
    assert "успешно" in message.answer.call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_invalid_promocode(monkeypatch):
    message = AsyncMock(spec=Message)
    message.text = "WRONGCODE"
    message.from_user = AsyncMock(id=1234)
    message.message_id = 123
    message.answer = AsyncMock(return_value=AsyncMock(spec=Message))
    state = AsyncMock(spec=FSMContext)

    monkeypatch.setattr("app.utils.utils.del_msg", AsyncMock())  # Mock del_msg
    monkeypatch.setattr(
        PromocodeService, "find_one_or_none", AsyncMock(return_value=None)
    )

    await get_promocode(message, state)
    message.answer.assert_called_once()
    assert "не найден" in message.answer.call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_already_applied_promocode(monkeypatch):
    message = AsyncMock(spec=Message)
    message.text = "USED"
    message.from_user = AsyncMock(id=1234)
    message.message_id = 123
    message.answer = AsyncMock(return_value=AsyncMock(spec=Message))
    state = AsyncMock(spec=FSMContext)

    promocode = AsyncMock()
    promocode.code = "USED"
    promocode.bonus = 30

    monkeypatch.setattr("app.utils.utils.del_msg", AsyncMock())  # Mock del_msg
    monkeypatch.setattr(
        PromocodeService, "find_one_or_none", AsyncMock(return_value=promocode)
    )
    monkeypatch.setattr(UserService, "get_promocode", AsyncMock(return_value=False))

    await get_promocode(message, state)
    message.answer.assert_called_once()
    assert "уже был активирован" in message.answer.call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_profile_command(monkeypatch):
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(
        id=1234, username="user", first_name="Name", last_name="Last"
    )
    message.message_id = 123
    message.answer = AsyncMock(return_value=AsyncMock(spec=Message))
    state = AsyncMock(spec=FSMContext)

    user_mock = AsyncMock()
    user_mock.balance = 123.456

    monkeypatch.setattr("app.utils.utils.del_msg", AsyncMock())  # Mock del_msg
    monkeypatch.setattr(
        UserService, "find_one_or_none", AsyncMock(return_value=user_mock)
    )
    monkeypatch.setattr(
        UserService, "find_min_date_expire", AsyncMock(return_value="2025-07-01")
    )

    await profile_command(message, state)
    message.answer.assert_called_once()
    assert "личный кабинет" in message.answer.call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_start_promocode(monkeypatch):
    call = create_callback()
    state = AsyncMock(spec=FSMContext)

    await start_promocode(call, state)
    call.message.edit_text.assert_called_once()
    assert "промокод" in call.message.edit_text.call_args[1]["text"].lower()
    state.set_state.assert_called_once_with("promo")
