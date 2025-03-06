from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from datetime import datetime

class Key(Base):
    __tablename__ = 'keys'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(
        back_populates = 'keys'
        )
    
    server_id: Mapped[int] = mapped_column(ForeignKey('servers.id'))
    server: Mapped['Server'] = relationship(
        back_populates='keys',
        lazy='selectin',
        )
    
    id_panel: Mapped[int]
    value: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)