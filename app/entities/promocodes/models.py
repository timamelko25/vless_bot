from typing import List
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.database import Base


class Promocode(Base):
    __tablename__ = 'promocodes'

    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    count: Mapped[int] = mapped_column(nullable=False, unique=False, default=0)
    bonus: Mapped[float] = mapped_column(
        nullable=False, unique=False, default=0)
