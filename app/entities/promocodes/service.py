from app.service.base import BaseService
from .models import Promocode
from .schemas import PromocodeScheme


class PromocodeService(BaseService):
    model = Promocode

    @classmethod
    async def update_count(cls, code: str):
        try:
            promocode = await cls.find_one_or_none(code=code)
            if promocode is None:
                return 0
            if promocode.count <= 0:
                raise ValueError("Promocode count cannot be decremented further")

            info = await cls.update(
                filter_by={"code": code},
                count=(promocode.count - 1),
            )

            return info
        except Exception as e:
            raise e

    @classmethod
    async def generate_promocode(cls, data: PromocodeScheme):
        try:
            info = await cls.add(**data.model_dump())

            return info
        except Exception as e:
            raise e