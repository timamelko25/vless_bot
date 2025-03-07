from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


from typing import List


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    balance: Mapped[float] = mapped_column(nullable=False, default=0)
    refer_id: Mapped[str] = mapped_column(unique=True)
    count_refer: Mapped[int] = mapped_column(default=0)
    description: Mapped[str] = mapped_column(nullable=True)
    
    keys: Mapped[List['Key']] = relationship(
        "Key",
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

    extend_existing = True