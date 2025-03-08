from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import class_mapper

from typing import List


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    
    balance: Mapped[float] = mapped_column(nullable=False, default=0)
    
    refer_id: Mapped[str] = mapped_column(nullable=True)
    count_refer: Mapped[int] = mapped_column(nullable=False, default=0)
    
    description: Mapped[str] = mapped_column(nullable=True)

    keys: Mapped[List['Key']] = relationship(
        "Key",
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

    extend_existing = True

    def to_dict(self) -> dict:
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}
