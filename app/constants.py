from enum import Enum

ACCESS_TOKEN = 'access_token'
REFRESH_TOKEN = 'refresh_token'
VERIFICATION_TOKEN = 'verification_token'


class TokenType(str, Enum):
    ACCESS = ACCESS_TOKEN
    REFRESH = REFRESH_TOKEN
    VERIFICATION = VERIFICATION_TOKEN


VERIFICATION_URL = "http://localhost:5000/api/v1/auth/verify_email/{token}"

USER_ROLE = 'user'
ADMIN_ROLE = 'admin'


class RoleType(str, Enum):
    USER = USER_ROLE
    ADMIN = ADMIN_ROLE


REVOKED = 'revoked'
