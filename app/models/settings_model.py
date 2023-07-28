import uuid

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.dialects.postgresql import UUID

from .base_model import BaseModel
from .users_model import RefUserMixin


class Settings(RefUserMixin, BaseModel):
    __tablename__ = 'settings'

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    notifications: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    dark_mode: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    language: Mapped[str] = Column(String, nullable=False, default='en')
    timezone: Mapped[str] = Column(String, nullable=False, default='UTC')
    country: Mapped[str] = Column(String, nullable=False, default='US')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.user!r})"
