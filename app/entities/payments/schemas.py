from pydantic import BaseModel


class PaymentScheme(BaseModel):
    user_id: int
    payment_id: str
    sum: float
