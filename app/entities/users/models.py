from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[str] = mapped_column(unique=True, nullable=False)

    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)

    balance: Mapped[float] = mapped_column(nullable=False, default=0)

    refer_id: Mapped[str] = mapped_column(nullable=True)
    count_refer: Mapped[int] = mapped_column(nullable=False, default=0)

    description: Mapped[str] = mapped_column(nullable=True)

    keys: Mapped[List["Key"]] = relationship(  # type: ignore  # noqa: F821
        "Key",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    promocodes_activate: Mapped[List["Promocode"]] = relationship(  # noqa: F821 # type: ignore
        "Promocode",
        secondary="promo_user",
        back_populates="users_activate",
        lazy="selectin",
    )

    extend_existing = True
