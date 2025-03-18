
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.database import Base


class HistoryPayment(Base):
    __tablename__ = 'history_payments'

    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    payment_id: Mapped[str]
    sum: Mapped[float]
