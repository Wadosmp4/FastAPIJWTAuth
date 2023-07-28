import uuid

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base_model import BaseModel

from app.constants import RoleType


class Users(BaseModel):
    __tablename__ = 'users'

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    username: Mapped[str] = Column(String, unique=True, nullable=False)
    name: Mapped[str] = Column(String,  nullable=False)
    email: Mapped[str] = Column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = Column(String, nullable=False)
    verified: Mapped[bool] = Column(Boolean, nullable=False, server_default='False')
    role: Mapped[RoleType] = Column(String, server_default=RoleType.USER, nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"


class RefUserMixin:
    @declared_attr
    def user_id(cls):
        return Column('user_id', ForeignKey('users.id', ondelete='CASCADE'))

    @declared_attr
    def user(cls):
        return relationship(Users,
                            primaryjoin=lambda: Users.id == cls.user_id,
                            passive_deletes=True,
                            backref='settings')
