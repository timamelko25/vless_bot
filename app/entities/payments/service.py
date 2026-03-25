from app.service.base import BaseService
from .models import HistoryPayment
from .schemas import PaymentScheme


class PaymentService(BaseService):
    model = HistoryPayment

    @classmethod
    async def add_payment_in_history(cls, data: PaymentScheme):
        info = await cls.add(**data.model_dump())

        return info
