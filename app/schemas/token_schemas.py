import uuid

from pydantic import BaseModel


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: str


class TokenData(BaseModel):
    sub: str
    user_id: str
    user_role: str
    token_type: str
    jti: str
    exp: int


class UserData(BaseModel):
    username: str
    user_id: uuid.UUID
    user_role: str
