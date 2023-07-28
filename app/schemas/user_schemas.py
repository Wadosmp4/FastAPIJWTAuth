import uuid

from datetime import datetime
from pydantic import BaseModel, EmailStr, constr

from app.config import config
from app.constants import RoleType


class UserBaseSchema(BaseModel):
    username: str
    name: str
    email: EmailStr


class RegisterUserSchema(UserBaseSchema):
    hashed_password: constr(regex=config.PASSWORD_REGEX)
    role: RoleType = RoleType.USER
    verified: bool = False


class CreateUserSchema(UserBaseSchema):
    verified: bool = False


class UpdateUserSchema(UserBaseSchema):
    role: RoleType
    verified: bool


class ResponseUserSchema(UserBaseSchema):
    id: uuid.UUID
    role: RoleType
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
