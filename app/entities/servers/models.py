from typing import List
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


from datetime import datetime

class Server(Base):
    __tablename__ = 'servers'
    
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    name_in_bot: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    
    keys: Mapped[List["Key"]] = relationship(
        "Key",
        back_populates='server',
        lazy='selectin',
        cascade='all, delete-orphan',
        )
    
    extend_existing = True