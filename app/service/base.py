from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper

from app.config import connection


class BaseService:
    """
    Базовый сервис для работы с моделями SQLAlchemy.
    Определяет стандартные CRUD-методы:
    - `find_all` — получить все записи по фильтру.
    - `find_one_or_none` — получить одну запись или None по фильтру.
    - `add` — добавить новую запись в базу данных.
    - `update` — обновляет запись в базе данных.
    - 'to_dict'  - Универсальный метод для конвертации объекта SQLAlchemy в словарь
    """

    model = None

    @classmethod
    @connection()
    async def find_all(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    @connection()
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    @connection()
    async def add(cls, session: AsyncSession, **values):
        new_instance = cls.model(**values)
        session.add(new_instance)
        await session.flush()
        return new_instance

    @classmethod
    @connection()
    async def update(cls, session: AsyncSession, filter_by, **values):
        query = (
            update(cls.model)
            .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(query)
        await session.flush()
        return result.rowcount

    def to_dict(self) -> dict:
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}
