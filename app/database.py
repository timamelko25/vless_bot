from functools import wraps
from typing import Annotated
from datetime import datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, text, TIMESTAMP
from sqlalchemy.orm import declared_attr, DeclarativeBase, Mapped, mapped_column

from .config import PG_URL


int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    """

    __abstract__ = True
    id: Mapped[int_pk]

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


engine = create_async_engine(url=PG_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


def connection(isolation_level: str | None = None, commit: bool = True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with async_session_maker() as session:
                try:
                    if isolation_level:
                        await session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))
                    result = await func(session=session, *args, **kwargs)
                    if commit:
                        await session.commit()
                    return result
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e

        return wrapper
    return decorator
