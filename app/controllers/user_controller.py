from typing import Dict

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import RegisterUserSchema
from app.models.users_model import Users
from app.utils import ProcessPassword

from .base_controller import BaseController
from .settings_controller import SettingsController


class UserController(BaseController):
    model = Users

    @classmethod
    async def create(cls, db: AsyncSession, data: Dict) -> model:
        user_instance = await super().create(db, data)
        user_settings = await SettingsController.create(db, {'user_id': user_instance.id})
        db.add_all([user_instance, user_settings])
        await db.commit()
        await db.refresh(user_instance)
        return user_instance

    @classmethod
    async def get_by_username(cls, db: AsyncSession, username: str) -> model:
        return (await db.execute(
            select(cls.model).filter(cls.model.username == username)
        )).scalar()

    @classmethod
    async def authenticate_user(cls, db: AsyncSession, username: str, password: str):
        user = await cls.get_by_username(db, username)
        if not user:
            return False
        if not ProcessPassword.verify_password(password, user.hashed_password):
            return False
        return user

    @classmethod
    async def verify_user(cls, db: AsyncSession, user: Users):
        user.verified = True
        db.add(user)
        await db.commit()

    @staticmethod
    def transform_payload(payload: RegisterUserSchema):
        payload.hashed_password = ProcessPassword.hash_password(payload.hashed_password)
        payload.verified = False
        payload.email = EmailStr(payload.email.lower())
        return payload
