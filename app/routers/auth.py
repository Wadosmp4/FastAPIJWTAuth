from fastapi import BackgroundTasks, APIRouter, status, Depends, Path
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils import ProcessToken, VERIFICATION_TOKEN_EXPIRES_IN, ACCESS_TOKEN_EXPIRES_IN
from app.cache import redis_client
from app.email import Email
from app.controllers import UserController
from app.dependencies import check_token_revocation
from app.schemas import RegisterUserSchema, ResponseUserSchema, TokensResponse, StatusResponse
from app.oauth2 import oauth2_scheme
from app.constants import REVOKED, TokenType, VERIFICATION_URL
from app.exceptions import ConflictException, ForbiddenException, UnauthorizedException, BadRequestException


router = APIRouter(prefix="/auth", tags=['Authentication'])


@router.post('/register', status_code=status.HTTP_201_CREATED,
             response_model=ResponseUserSchema)
async def register_user(payload: RegisterUserSchema,
                        background_tasks: BackgroundTasks,
                        db: AsyncSession = Depends(get_db)):
    user = await UserController.get_by_username(db, payload.username)
    if user:
        raise ConflictException(detail='Account already exist')

    payload = UserController.transform_payload(payload)
    new_user = await UserController.create(db, payload.dict())
    user_info = {'sub': new_user.username, 'user_id': str(new_user.id), 'user_role': new_user.role}

    token_payload = ProcessToken.create_token_payload(user_info,
                                                      VERIFICATION_TOKEN_EXPIRES_IN,
                                                      TokenType.VERIFICATION)
    token = ProcessToken.create_token(token_payload, TokenType.VERIFICATION)

    verification_url = VERIFICATION_URL.format(token=token)
    email = Email(payload.name, verification_url, [payload.email])
    background_tasks.add_task(email.send_verification_code)

    return new_user


@router.get('/verify_email/{token}')
async def verify_email(db: AsyncSession = Depends(get_db),
                       token: str = Path()):
    token_data = ProcessToken.validate_token(token, TokenType.VERIFICATION)
    user = await UserController.get_by_username(db, token_data.sub)
    if not user or user.verified:
        raise ForbiddenException(detail='Invalid verification code or account already verified')
    await UserController.verify_user(db, user)

    return {
        "status": "success",
        "message": "Account verified successfully"
    }


@router.post('/token', status_code=status.HTTP_200_OK,
             response_model=TokensResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    user = await UserController.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise BadRequestException(detail='Incorrect Email or Password')

    if not user.verified:
        raise UnauthorizedException(detail='Please verify your email address')

    user_info = {'sub': user.username, 'user_id': str(user.id), 'user_role': user.role}
    access_and_refresh_tokens = ProcessToken.create_access_and_refresh_tokens(user_info)

    return {**access_and_refresh_tokens,
            'expires_in': ACCESS_TOKEN_EXPIRES_IN.total_seconds(),
            'token_type': 'Bearer'}


@router.post('/token/refresh', status_code=status.HTTP_200_OK,
             response_model=TokensResponse,
             dependencies=[Depends(check_token_revocation(TokenType.REFRESH))])
async def refresh_access_token(db: AsyncSession = Depends(get_db),
                               refresh_token: oauth2_scheme = Depends()):
    token_data = ProcessToken.validate_token(refresh_token, token_type=TokenType.REFRESH)

    user = await UserController.get(db, str(token_data.user_id))
    if not user:
        raise UnauthorizedException(detail='The user belonging to this token no longer exist')

    user_info = {'sub': user.username, 'user_id': str(user.id), 'user_role': user.role}
    access_and_refresh_tokens = ProcessToken.create_access_and_refresh_tokens(user_info)

    return {**access_and_refresh_tokens,
            'expires_in': ACCESS_TOKEN_EXPIRES_IN.total_seconds(),
            'token_type': 'Bearer'}


@router.get('/token/verify',
            status_code=status.HTTP_200_OK,
            response_model=ResponseUserSchema,
            dependencies=[Depends(check_token_revocation(TokenType.ACCESS))])
async def get_me(db: AsyncSession = Depends(get_db),
                 token: oauth2_scheme = Depends()):
    token_data = ProcessToken.validate_token(token, token_type=TokenType.ACCESS)

    user = await UserController.get(db, str(token_data.user_id))
    if not user:
        raise UnauthorizedException(detail='The user belonging to this token no longer exist')
    return user


@router.delete('/revoke/access',
               status_code=status.HTTP_200_OK,
               response_model=StatusResponse,
               dependencies=[Depends(check_token_revocation(TokenType.ACCESS))])
async def access_revoke(token: oauth2_scheme = Depends()):
    token_data = ProcessToken.validate_token(token, token_type=TokenType.ACCESS)
    jti = token_data.jti
    await redis_client.setex(jti, ACCESS_TOKEN_EXPIRES_IN, REVOKED)
    return {'status': 'success', 'message': 'Access token revoked'}


@router.delete('/revoke/refresh',
               status_code=status.HTTP_200_OK,
               response_model=StatusResponse,
               dependencies=[Depends(check_token_revocation(TokenType.REFRESH))])
async def refresh_revoke(token: oauth2_scheme = Depends()):
    token_data = ProcessToken.validate_token(token, token_type=TokenType.REFRESH)
    jti = token_data.jti
    await redis_client.setex(jti, ACCESS_TOKEN_EXPIRES_IN, REVOKED)
    return {'status': 'success', 'message': 'Refresh token revoked'}
