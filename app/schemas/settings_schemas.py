import uuid

from pydantic import BaseModel


class SettingsBaseSchema(BaseModel):
    notifications: bool
    dark_mode: bool
    language: str
    timezone: str
    country: str


class CreateSettingsSchema(SettingsBaseSchema):
    user_id: uuid.UUID


class ResponseSettingsSchema(CreateSettingsSchema):

    class Config:
        orm_mode = True


class UpdateSettingsSchema(CreateSettingsSchema):
    pass
