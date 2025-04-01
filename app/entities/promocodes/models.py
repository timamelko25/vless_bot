from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, ForeignKey, Integer

from app.database import Base
from app.entities.users.models import User

PromoUser = Table(
    "promo_user",
    Base.metadata,
    Column("promo_id", Integer, ForeignKey("promocodes.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class Promocode(Base):
    __tablename__ = "promocodes"

    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    count: Mapped[int] = mapped_column(nullable=False, unique=False, default=0)
    bonus: Mapped[float] = mapped_column(nullable=False, unique=False, default=0)
    users_activate: Mapped[List["User"]] = relationship(
        "User",
        secondary="promo_user",
        back_populates="promocodes_activate",
        lazy="selectin",
    )
