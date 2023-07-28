from fastapi import Depends

from app.dependencies import get_current_user
from app.models import Users
from app.constants import RoleType

from app.exceptions import ForbiddenException


class RoleChecker:
    def __init__(self, allowed_roles: list[RoleType]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: Users = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise ForbiddenException(detail="Operation not permitted")


allow_manage_everything = RoleChecker([RoleType.ADMIN])
