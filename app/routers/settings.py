from fastapi import Path, status, APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ResponseSettingsSchema, CreateSettingsSchema, UpdateSettingsSchema, StatusResponse
from app.controllers import SettingsController
from app.dependencies import check_token_revocation, get_current_user
from app.roles import allow_manage_everything
from app.models import Users
from app.constants import TokenType
from app.exceptions import NotFoundException, ConflictException

router = APIRouter(prefix='/users/settings',
                   tags=['Settings'],
                   dependencies=[Depends(check_token_revocation(TokenType.ACCESS))])


@router.get('/', status_code=status.HTTP_200_OK,
            response_model=ResponseSettingsSchema)
async def get_my_settings(db: AsyncSession = Depends(get_db),
                          user: Users = Depends(get_current_user)):
    if not user:
        raise NotFoundException(detail=f'User not found')
    settings = await SettingsController.get_by_user_id(db, user.id)
    return settings


@router.put('/', status_code=status.HTTP_200_OK,
            response_model=ResponseSettingsSchema)
async def update_my_settings(payload: UpdateSettingsSchema,
                             db: AsyncSession = Depends(get_db),
                             user: Users = Depends(get_current_user)):
    if not user:
        raise NotFoundException(detail=f'User not found')
    settings = await SettingsController.get_by_user_id(db, user.id)
    if not settings:
        raise NotFoundException(detail='Settings does not exist')
    updated_settings = await SettingsController.update(db, settings, payload.dict())
    return updated_settings


@router.get('/all', status_code=status.HTTP_200_OK,
            response_model=list[ResponseSettingsSchema],
            dependencies=[Depends(allow_manage_everything)])
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    settings = await SettingsController.all(db)
    return settings


@router.post('/', status_code=status.HTTP_201_CREATED,
             response_model=ResponseSettingsSchema,
             dependencies=[Depends(allow_manage_everything)])
async def create_settings(payload: CreateSettingsSchema,
                          db: AsyncSession = Depends(get_db)):
    settings = await SettingsController.get_by_user_id(db, payload.user_id)
    if settings:
        raise ConflictException(detail='Settings for this user already exist')

    new_settings = await SettingsController.create(db, payload.dict())
    return new_settings


@router.put('/{settings_id}', status_code=status.HTTP_200_OK,
            response_model=ResponseSettingsSchema,
            dependencies=[Depends(allow_manage_everything)])
async def update_settings(payload: UpdateSettingsSchema,
                          db: AsyncSession = Depends(get_db),
                          settings_id: str = Path()):
    settings = await SettingsController.get(db, settings_id)
    if not settings:
        raise NotFoundException(detail='Settings does not exist')
    updated_settings = await SettingsController.update(db, settings, payload.dict())
    return updated_settings


@router.delete('/{settings_id}', status_code=status.HTTP_200_OK,
               response_model=StatusResponse,
               dependencies=[Depends(allow_manage_everything)])
async def delete_settings(db: AsyncSession = Depends(get_db),
                          settings_id: str = Path()):
    settings = await SettingsController.get(db, settings_id)
    if not settings:
        raise NotFoundException(detail='User does not exist')

    await SettingsController.delete(db, settings)
    return {'status': 'success', 'message': 'Settings deleted successfully'}
