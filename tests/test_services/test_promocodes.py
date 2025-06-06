import pytest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from app.entities.promocodes.service import PromocodeService
from app.entities.promocodes.schemas import PromocodeScheme

# Sample promocode data for testing
promocode_data = {
    "code": "TEST123",
    "count": 10,
    "bonus": 20.0,
}


@pytest.mark.asyncio
async def test_find_all_promocodes_empty():
    # Test retrieving all promocodes when none exist
    result = await PromocodeService.find_all()
    assert result == []


@pytest.mark.asyncio
async def test_generate_promocode_success():
    # Test successful promocode creation
    promocode = PromocodeScheme(**promocode_data)
    result = await PromocodeService.generate_promocode(promocode)
    assert result.code == "TEST123"
    assert result.count == 10
    assert result.bonus == 20.0


@pytest.mark.asyncio
async def test_generate_promocode_error():
    # Test promocode creation with database error
    with patch(
        "app.entities.promocodes.models.Promocode.__init__",
        side_effect=SQLAlchemyError("Add failed"),
    ):
        promocode = PromocodeScheme(**promocode_data)
        with pytest.raises(SQLAlchemyError):
            await PromocodeService.generate_promocode(promocode)


@pytest.mark.asyncio
async def test_update_count_success():
    # Test successful count update
    result = await PromocodeService.update_count(code="TEST123")
    assert result == 1  # 1 row affected
    updated_promocode = await PromocodeService.find_one_or_none(code="TEST123")
    assert updated_promocode.count == 9  # Count decremented by 1


@pytest.mark.asyncio
async def test_update_count_not_found():
    # Test updating count for non-existent promocode
    result = await PromocodeService.update_count(code="NONEXISTENT")
    assert result == 0  # 0 rows affected


@pytest.mark.asyncio
async def test_update_count_zero_count():
    # Test updating count when promocode count is already 0
    zero_count_data = {"code": "ZERO123", "count": 0, "bonus": 15.0}
    promocode = PromocodeScheme(**zero_count_data)
    await PromocodeService.generate_promocode(promocode)
    with pytest.raises(
        ValueError, match="Promocode count cannot be decremented further"
    ):
        await PromocodeService.update_count(code="ZERO123")


@pytest.mark.asyncio
async def test_update_count_error():
    # Test database error during count update
    with patch(
        "app.entities.promocodes.service.PromocodeService.update",
        side_effect=SQLAlchemyError("Update failed"),
    ):
        with pytest.raises(SQLAlchemyError):
            await PromocodeService.update_count(code="TEST123")


@pytest.mark.asyncio
async def test_find_all_promocodes_with_data():
    # Test retrieving all promocodes with existing data
    promocode1 = PromocodeScheme(code="PROMO1", count=5, bonus=10.0)
    promocode2 = PromocodeScheme(code="PROMO2", count=8, bonus=15.0)
    await PromocodeService.generate_promocode(promocode1)
    await PromocodeService.generate_promocode(promocode2)
    result = await PromocodeService.find_all()
    assert isinstance(result, list)
    assert any(p.code == "PROMO1" for p in result)
    assert any(p.code == "PROMO2" for p in result)


@pytest.mark.asyncio
async def test_find_all_promocodes_error():
    # Test database error during find_all
    with patch(
        "app.entities.promocodes.service.PromocodeService.find_all",
        side_effect=SQLAlchemyError("Find all failed"),
    ):
        with pytest.raises(SQLAlchemyError):
            await PromocodeService.find_all()


@pytest.mark.asyncio
async def test_find_one_or_none_promocode():
    # Test finding a single promocode
    result = await PromocodeService.find_one_or_none(code="TEST123")
    assert result.code == "TEST123"
    assert result.count == 9
    assert result.bonus == 20.0


@pytest.mark.asyncio
async def test_find_one_or_none_not_found():
    # Test finding non-existent promocode
    result = await PromocodeService.find_one_or_none(code="NONEXISTENT")
    assert result is None


@pytest.mark.asyncio
async def test_update_promocode_success():
    # Test successful promocode update
    result = await PromocodeService.update(
        filter_by={"code": "TEST123"}, count=5, bonus=25.0
    )
    assert result == 1  # 1 row affected
    updated_promocode = await PromocodeService.find_one_or_none(code="TEST123")
    assert updated_promocode.count == 5
    assert updated_promocode.bonus == 25.0


@pytest.mark.asyncio
async def test_delete_promocode_success():
    # Test successful promocode deletion
    result = await PromocodeService.delete(code="TEST123")
    assert result == 1  # 1 row affected
    deleted_promocode = await PromocodeService.find_one_or_none(code="TEST123")
    assert deleted_promocode is None


@pytest.mark.asyncio
async def test_delete_promocode_not_found():
    # Test deleting non-existent promocode
    result = await PromocodeService.delete(code="NONEXISTENT")
    assert result == 0  # 0 rows affected


@pytest.mark.asyncio
async def test_delete_promocode_error():
    # Test database error during deletion
    with patch(
        "app.entities.promocodes.service.PromocodeService.delete",
        side_effect=SQLAlchemyError("Delete failed"),
    ):
        with pytest.raises(SQLAlchemyError):
            await PromocodeService.delete(code="TEST123")


@pytest.mark.asyncio
async def test_delete_all_promocodes_fails():
    # Test prevention of mass deletion
    with pytest.raises(ValueError, match="Enter at least 1 parameter"):
        await PromocodeService.delete(delete_all=False)


@pytest.mark.asyncio
async def test_update_promocode_not_found():
    # Test updating non-existent promocode
    result = await PromocodeService.update(filter_by={"code": "NONEXISTENT"}, count=5)
    assert result == 0  # 0 rows affected


@pytest.mark.asyncio
async def test_update_promocode_error():
    # Test database error during update
    with patch(
        "app.entities.promocodes.service.PromocodeService.update",
        side_effect=SQLAlchemyError("Update failed"),
    ):
        with pytest.raises(SQLAlchemyError):
            await PromocodeService.update(filter_by={"code": "TEST123"}, count=5)
