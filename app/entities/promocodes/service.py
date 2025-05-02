from app.service.base import BaseService
from .models import Promocode
from .schemas import PromocodeScheme


class PromocodeService(BaseService):
    model = Promocode

    @classmethod
    async def update_count(cls, code: str):
        promocode = await cls.find_one_or_none(code=code)

        info = await cls.update(
            filter_by={"code": code},
            count=(promocode.count - 1),
        )

        return info

    @classmethod
    async def generate_promocode(cls, data: PromocodeScheme):
        info = await cls.add(**data.model_dump())

        return info
