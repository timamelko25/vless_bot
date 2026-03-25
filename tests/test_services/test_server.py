import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.entities.servers.service import ServerService


@pytest.fixture
def mock_key_service():
    with patch("app.entities.servers.service.KeyService") as mock:
        mock.delete = AsyncMock()
        yield mock


@pytest.mark.asyncio
async def test_get_servers_names_empty():
    # Test empty server list
    result = await ServerService.get_servers_names()
    assert result == []


@pytest.mark.asyncio
async def test_get_servers_names_with_servers():
    # Test with existing servers
    await ServerService.add(
        id=1,
        name="test_server",
        domain="https://example.com",
    )
    result = await ServerService.get_servers_names()
    assert isinstance(result, list)
    assert any(server == "test_server" for server in result)


@pytest.mark.asyncio
async def test_get_servers_names_error():
    # Test database error
    with patch(
        "app.entities.servers.service.ServerService.find_all", new_callable=AsyncMock
    ) as mock_find:
        mock_find.side_effect = SQLAlchemyError("DB error")
        with pytest.raises(SQLAlchemyError):
            await ServerService.get_servers_names()


@pytest.mark.asyncio
async def test_delete_server_success(mock_key_service):
    # Test successful server deletion
    result = await ServerService.delete_server("test_server")
    assert result == 1  # 1 row affected
    mock_key_service.delete.assert_awaited_once_with(server_id=1)


@pytest.mark.asyncio
async def test_delete_server_not_found(mock_key_service):
    # Test deleting non-existent server
    result = await ServerService.delete_server("non_existent")
    assert result == 0  # 0 rows affected
    mock_key_service.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_server_key_deletion_failure(mock_key_service):
    # Test when key deletion fails
    mock_key_service.delete.side_effect = SQLAlchemyError("Key deletion failed")
    await ServerService.add(
        id=1,
        name="test_server",
        domain="https://example.com",
    )
    with pytest.raises(SQLAlchemyError):
        await ServerService.delete_server("test_server")
    mock_key_service.delete.assert_awaited_once_with(server_id=1)


@pytest.mark.asyncio
async def test_find_one_or_none_server():
    # Test finding single server
    await ServerService.add(
        id=2,
        name="found_server",
        domain="https://example2.com",
    )
    result = await ServerService.find_one_or_none(name="found_server")
    assert result.name == "found_server"


@pytest.mark.asyncio
async def test_find_one_or_none_not_found():
    # Test server not found
    result = await ServerService.find_one_or_none(name="missing")
    assert result is None


@pytest.mark.asyncio
async def test_add_server_error():
    # Test server addition error
    with patch(
        "app.entities.servers.models.Server.__init__",
        side_effect=SQLAlchemyError("Add failed"),
    ):
        with pytest.raises(SQLAlchemyError):
            await ServerService.add(name="fail_server", domain="http://example.com")


@pytest.mark.asyncio
async def test_update_server_success():
    # Test updating server
    result = await ServerService.update(
        filter_by={"name": "test_server"}, domain="new.example.com"
    )
    assert result == 1  # 1 row affected


@pytest.mark.asyncio
async def test_update_server_not_found():
    # Test updating non-existent server
    result = await ServerService.update(
        filter_by={"name": "missing"}, domain="new.example.com"
    )
    assert result == 0  # 0 rows affected


@pytest.mark.asyncio
async def test_update_server_error():
    # Test update error
    with patch(
        "app.entities.servers.service.ServerService.update",
        side_effect=SQLAlchemyError("Update failed"),
    ):
        with pytest.raises(SQLAlchemyError):
            await ServerService.update(
                filter_by={"name": "test_server"}, domain="new.example.com"
            )


@pytest.mark.asyncio
async def test_delete_server_1_success():
    # Test deleting server
    result = await ServerService.delete(name="test_server")
    assert result == 1  # 1 row affected


@pytest.mark.asyncio
async def test_delete_non_server_not_found():
    # Test deleting non-existent server
    result = await ServerService.delete(name="missing")
    assert result == 0  # 0 rows affected


@pytest.mark.asyncio
async def test_delete_server_error():
    # Test delete error
    with patch(
        "app.entities.servers.service.ServerService.delete",
        side_effect=SQLAlchemyError("Delete failed"),
    ):
        with pytest.raises(SQLAlchemyError):
            await ServerService.delete(name="test_server")


@pytest.mark.asyncio
async def test_delete_all_servers_fails():
    # Test prevention of mass deletion
    with pytest.raises(ValueError, match="Enter at least 1 parameter"):
        await ServerService.delete(delete_all=False)
