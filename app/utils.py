import uuid
from jose import jwt, JWTError

from passlib.context import CryptContext
from datetime import datetime, timedelta

from app.config import config
from app.schemas import TokenData
from app.constants import TokenType
from app.exceptions import UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRES_IN = timedelta(minutes=config.ACCESS_TOKEN_EXPIRES_IN)
REFRESH_TOKEN_EXPIRES_IN = timedelta(minutes=config.REFRESH_TOKEN_EXPIRES_IN)
VERIFICATION_TOKEN_EXPIRES_IN = timedelta(minutes=config.VERIFICATION_TOKEN_EXPIRES_IN)


class ProcessPassword:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)


class ProcessToken:
    TOKEN_CONFIG = {
        TokenType.ACCESS: (config.JWT_PUBLIC_KEY, config.JWT_ALGORITHM),
        TokenType.REFRESH: (config.JWT_PRIVATE_KEY, config.JWT_ALGORITHM),
        TokenType.VERIFICATION: (config.VERIFICATION_SECRET_KEY, config.VERIFICATION_ALGORITHM)
    }

    @staticmethod
    def create_token_payload(user_info: dict,
                             expires_delta: timedelta,
                             token_type: TokenType = TokenType.ACCESS) -> dict:
        expires = datetime.utcnow() + expires_delta
        encode = {**user_info,
                  'token_type': token_type,
                  'jti': str(uuid.uuid4()),
                  'exp': expires.timestamp()}
        return encode

    @staticmethod
    def create_token(encode: dict, token_type: TokenType) -> str:
        secret_key, algorithm = ProcessToken.TOKEN_CONFIG[token_type]
        token = jwt.encode(encode, secret_key, algorithm=algorithm)
        return token

    @staticmethod
    def create_access_and_refresh_tokens(user_info: dict) -> dict:
        access_token_payload = ProcessToken.create_token_payload(user_info=user_info,
                                                                 expires_delta=ACCESS_TOKEN_EXPIRES_IN,
                                                                 token_type=TokenType.ACCESS)
        refresh_token_payload = ProcessToken.create_token_payload(user_info=user_info,
                                                                  expires_delta=REFRESH_TOKEN_EXPIRES_IN,
                                                                  token_type=TokenType.REFRESH)
        access_token = ProcessToken.create_token(access_token_payload, TokenType.ACCESS)
        refresh_token = ProcessToken.create_token(refresh_token_payload, TokenType.REFRESH)
        return {'access_token': access_token, 'refresh_token': refresh_token}

    @staticmethod
    def decode_token(token: str, token_type: TokenType = TokenType.ACCESS) -> dict:
        try:
            secret_key, algorithm = ProcessToken.TOKEN_CONFIG[token_type]
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        except JWTError:
            raise UnauthorizedException(detail='Could not validate a user')
        return payload

    @staticmethod
    def validate_token(token: str, token_type: TokenType = TokenType.ACCESS) -> TokenData:
        payload = ProcessToken.decode_token(token, token_type)
        token_data = TokenData(**payload)

        if token_data.sub is None or token_data.user_id is None:
            raise UnauthorizedException(detail='Could not validate a user')

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise UnauthorizedException(detail="Token expired")

        return token_data
