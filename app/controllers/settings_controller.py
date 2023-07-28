from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models import Settings

from .base_controller import BaseController


class SettingsController(BaseController):
    model = Settings

    @classmethod
    async def get_by_user_id(cls, db: AsyncSession, user_id: UUID) -> model:
        return (await db.execute(
            select(cls.model).filter(cls.model.user_id == user_id)
        )).scalar()
