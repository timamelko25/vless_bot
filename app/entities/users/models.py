from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(nullable=True)
    balance: Mapped[int] = mapped_column(nullable=False, default=0)
    keys: Mapped[list['Key']] = relationship(
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan',
        )
    description: Mapped[str] = mapped_column(nullable=True)