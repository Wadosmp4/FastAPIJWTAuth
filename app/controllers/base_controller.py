import inspect

from abc import ABC
from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base_model import Base


class TransactionMeta(type):
    def __new__(cls, name, bases, dct):
        for method_name, method in dct.items():
            if inspect.iscoroutinefunction(method):
                dct[method_name] = cls.wrap_with_transaction(method)

        return super(TransactionMeta, cls).__new__(cls, name, bases, dct)

    @classmethod
    def wrap_with_transaction(cls, method):
        async def wrapper(self, db: AsyncSession, *args, **kwargs):
            async with db.begin():
                return method(self, db, *args, **kwargs)
        return wrapper


class BaseController(ABC):
    model = None
    __metaclass__ = TransactionMeta

    @classmethod
    async def create(cls, db: AsyncSession, data: Dict) -> model:
        new_instance = cls.model(**data)
        db.add(new_instance)
        await db.commit()
        await db.refresh(new_instance)
        return new_instance

    @classmethod
    async def get(cls, db: AsyncSession, obj_id: str) -> model:
        return (await db.execute(
            select(cls.model).filter(cls.model.id == obj_id)
        )).scalar()

    @classmethod
    async def all(cls, db: AsyncSession, filters: list = None) -> list:
        if not filters:
            filters = []
        return [el[0] for el in (await db.execute(select(cls.model).filter(*filters)))]

    @classmethod
    async def update(cls, db: AsyncSession, obj: Base, data: Dict) -> model:
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    @classmethod
    async def delete(cls, db: AsyncSession, obj) -> bool:
        await db.delete(obj)
        await db.commit()
        return True
