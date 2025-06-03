import pytest
import asyncio
import aiohttp
import os
import subprocess
import time
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from aiogram.types import Update, Message, Chat
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.database import Base, async_session_maker
from app.entities.users.service import UserService
from app.entities.users.models import User

user_data = {
    "telegram_id": 12345,
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "balance": 0.0,
    "count_refer": 0,
}


# UserService.add
@pytest.mark.asyncio
async def test_user_add():
    result = await UserService.add(**user_data)
    assert result is not None
    assert result.telegram_id == 12345
    assert result.username == "testuser"
    assert result.balance == 0.0


# UserService.find_one_or_none
@pytest.mark.asyncio
async def test_user_find():
    result = await UserService.find_one_or_none(telegram_id=12345)
    
    assert result is not None
    assert result.telegram_id == 12345
    assert result.username == "testuser"
    assert result.balance == 0.0


@pytest.mark.asyncio
async def test_user_update_balance():
    await UserService.update_balance(12345, 100)

    result = await UserService.find_one_or_none(telegram_id=12345)

    assert result is not None
    assert result.balance == 100


@pytest.mark.asyncio
async def test_user_update_count_refer():
    await UserService.update_count_refer(12345)

    result = await UserService.find_one_or_none(telegram_id=12345)

    assert result is not None
    assert result.count_refer == 1


@pytest.mark.asyncio
async def test_user_update_balance_count_refer():
    await UserService.update_balance_and_count_refer(12345, 100)

    result = await UserService.find_one_or_none(telegram_id=12345)

    assert result is not None
    assert result.count_refer == 2
    assert result.balance == 200
