from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Server(Base):
    __tablename__ = 'servers'

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    domain: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    keys: Mapped[List["Key"]] = relationship( # type: ignore
        "Key",
        back_populates='server',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

    extend_existing = True
