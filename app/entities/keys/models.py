from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.database import Base


class Key(Base):
    __tablename__ = "keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(  # type: ignore  # noqa: F821
        "User", back_populates="keys", lazy="selectin"
    )

    server_id: Mapped[str] = mapped_column(ForeignKey("servers.id"))
    server: Mapped["Server"] = relationship(  # type: ignore  # noqa: F821
        "Server", back_populates="keys", lazy="selectin"
    )

    id_panel: Mapped[str]
    email: Mapped[str]
    value: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[bool] = mapped_column(default=True)

    extend_existing = True
