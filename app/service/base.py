from typing import Dict

from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.future import select
from sqlalchemy.orm import class_mapper

from app.database import async_session_maker


class BaseService:
    """Base service class providing common database operations for SQLAlchemy models.

    This class should be subclassed, and the `model` attribute must be set to a SQLAlchemy
    model class. Provides async CRUD operations and basic query methods.

    Methods:
        find_all: Retrieve multiple records from the database.
        find_one_or_none: Fetch a single record or return None.
        add: Create and persist a new database record.
        update: Modify existing records based on filters.
        delete: Remove records from the database.
        to_dict: Convert model instance to dictionary representation.

    Attributes:
        model (DeclarativeBase): SQLAlchemy model class to operate on. Must be
            defined in subclasses.
    """

    model = None

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)  # type: ignore
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)  # type: ignore
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **values):
        async with async_session_maker() as session:
            new_instance = cls.model(**values)  # type: ignore
            session.add(new_instance)
            await session.commit()
            return new_instance

    @classmethod
    async def update(cls, filter_by: Dict, **values) -> int:
        async with async_session_maker() as session:
            query = (
                sqlalchemy_update(cls.model)  # type: ignore
                .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                .values(**values)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount

    @classmethod
    async def delete(cls, delete_all: bool = False, **filter_by) -> int:
        async with async_session_maker() as session:
            if not delete_all and not filter_by:
                raise ValueError("Enter at least 1 parameter")

            query = sqlalchemy_delete(cls.model).filter_by(**filter_by)  # type: ignore
            result = await session.execute(query)
            await session.commit()
            return result.rowcount

    def to_dict(self) -> dict:
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}
