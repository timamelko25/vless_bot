from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import class_mapper

from app.database import Base


class Key(Base):
    __tablename__ = 'keys'

    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship(
        "User",
        back_populates='keys'
    )

    server_id: Mapped[str] = mapped_column(ForeignKey('servers.id'))
    server: Mapped["Server"] = relationship(
        "Server",
        back_populates='keys',

    )

    id_panel: Mapped[str]
    email: Mapped[str]
    value: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[str] = mapped_column(nullable=False)

    extend_existing = True

    def to_dict(self) -> dict:
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}
