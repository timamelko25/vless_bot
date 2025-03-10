from sqlalchemy.ext.asyncio import AsyncSession

from app.service.base import BaseService
from app.database import connection
from .models import HistoryPayment

class PaymentService(BaseService):
    model = HistoryPayment
    
    @classmethod
    @connection()
    async def add_payment_in_history(cls, session: AsyncSession, data: dict):
        info = await cls.add(
            **data
            )
        
        await session.flush()
        return info