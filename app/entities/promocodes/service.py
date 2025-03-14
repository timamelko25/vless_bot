from sqlalchemy.ext.asyncio import AsyncSession

from app.service.base import BaseService
from app.database import connection
from .models import Promocode

class PromocodeService(BaseService):
    model = Promocode
    
    @classmethod
    @connection()
    async def update_count(cls, session: AsyncSession, code: str):
        
        promocode = await cls.find_one_or_none(code=code)
        
        info = await cls.update(
            filter_by={
                "code": code
                },
            count = promocode.count - 1
            )
        
        await session.flush()
        return info
    
    
    @classmethod
    @connection()
    async def generate_promocode(cls, session: AsyncSession, data: dict):
        info = await cls.add(
            **data
            )
        
        await session.flush()
        return info