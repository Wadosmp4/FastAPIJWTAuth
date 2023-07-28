from fastapi import Path, Query, status, APIRouter, Depends, Request

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.roles import allow_manage_everything
from app.schemas import ResponseUserSchema, RegisterUserSchema, UpdateUserSchema, StatusResponse
from app.controllers import UserController
from app.dependencies import check_token_revocation
from app.models import Users
from app.constants import TokenType
from app.exceptions import NotFoundException, ConflictException

router = APIRouter(prefix='/users',
                   tags=['Users'],
                   dependencies=[Depends(allow_manage_everything),
                                 Depends(check_token_revocation(TokenType.ACCESS))])


@router.get('/', status_code=status.HTTP_200_OK,
            response_model=list[ResponseUserSchema])
async def get_all_users(db: AsyncSession = Depends(get_db),
                        username: str = Query(required=False, default=None),
                        email: str = Query(required=False, default=None),
                        role: str = Query(required=False, default=None)):
    filters = []
    if username:
        filters.append(Users.username.ilike(f'%{username}%'))
    if email:
        filters.append(Users.email.ilike(f'%{email}%'))
    if role:
        filters.append(Users.role == role)

    users = await UserController.all(db, filters)
    if not users:
        raise NotFoundException(detail=f'No users found')
    return users


@router.post('/', status_code=status.HTTP_201_CREATED,
             response_model=ResponseUserSchema)
async def create_user(payload: RegisterUserSchema,
                      db: AsyncSession = Depends(get_db)):
    filter_by_username = (Users.username == payload.username)
    filter_by_email = (Users.email == payload.email)
    users = await UserController.all(db, [or_(filter_by_username, filter_by_email)])
    if users:
        raise ConflictException(detail='Account already exist')

    payload = UserController.transform_payload(payload)
    new_user = await UserController.create(db, payload.dict())
    return new_user


@router.get('/{user_id}', status_code=status.HTTP_200_OK,
            response_model=ResponseUserSchema)
async def get_user(user_id: str = Path(),
                   db: AsyncSession = Depends(get_db)):
    user = await UserController.get(db, user_id)
    if not user:
        raise NotFoundException(detail=f'No users with {user_id} id')
    return user


@router.put('/{user_id}', status_code=status.HTTP_200_OK,
            response_model=ResponseUserSchema)
async def update_user(request: Request, payload: UpdateUserSchema,
                      user_id: str = Path()):
    db = request.state.db
    user = await UserController.get(db, user_id)
    if not user:
        raise NotFoundException(detail='User does not exist')
    updated_user = await UserController.update(db, user, payload.dict())
    return updated_user


@router.delete('/{user_id}', status_code=status.HTTP_200_OK,
               response_model=StatusResponse)
async def delete_user(db: AsyncSession = Depends(get_db),
                      user_id: str = Path()):
    user = await UserController.get(db, user_id)
    if not user:
        raise NotFoundException(detail='User does not exist')

    await UserController.delete(db, user)
    return {'status': 'success', 'message': 'User deleted successfully'}
