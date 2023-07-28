from fastapi import Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import ProcessToken
from app.database import get_db
from app.controllers import UserController
from app.models import Users
from app.oauth2 import oauth2_scheme
from app.cache import token_in_deny_list
from app.constants import TokenType
from app.exceptions import UnauthorizedException


async def get_current_user(db: AsyncSession = Depends(get_db),
                           token: str = Depends(oauth2_scheme)) -> Users:
    token_data = ProcessToken.validate_token(token, token_type=TokenType.ACCESS)
    return await UserController.get(db, str(token_data.user_id))


def check_token_revocation(token_type: TokenType):
    async def check_id_token_revoked(request: Request):
        token = await oauth2_scheme(request)
        token_data = ProcessToken.validate_token(token, token_type=token_type)
        if await token_in_deny_list(token_data.jti):
            raise UnauthorizedException(detail="Token has been revoked")
    return check_id_token_revoked
