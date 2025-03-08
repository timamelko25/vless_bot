from typing import List
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


from datetime import datetime

class HistoryPayment(Base):
    __tablename__ = 'history_payments'
    
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    payment_id: Mapped[str]
    sum: Mapped[float]