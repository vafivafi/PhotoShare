from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from authx import TokenPayload

from src.infrastructure.db.session import DataBaseConfig
from src.infrastructure.secure.hash_service import ArgonService
from src.infrastructure.cloud_storage.s3_service import S3Service
from src.infrastructure.secure.authx_service import AuthXService
from src.infrastructure.db.repository.image_repository import ImageRepository
from src.infrastructure.db.repository.user_repositoty import UserRepository
from src.service.user_service import UserService
from src.service.image_service import ImageService


@lru_cache(maxsize=1)
def get_argon_service() -> ArgonService:
    return ArgonService()


@lru_cache(maxsize=1)
def get_s3_service() -> S3Service:
    return S3Service()


@lru_cache(maxsize=1)
def get_data_base_service() -> DataBaseConfig:
    return DataBaseConfig()


@lru_cache(maxsize=1)
def get_authx_service() -> AuthXService:
    return AuthXService()


def get_image_repository() -> ImageRepository:
    return ImageRepository()


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_user_service(
        user_repository: UserRepository = Depends(get_user_repository),
        password_service: ArgonService = Depends(get_argon_service),
        authx_service: AuthXService = Depends(get_authx_service),
) -> UserService:
    return UserService(
        user_repository=user_repository,
        password_service=password_service,
        auth_service=authx_service,
    )

def get_image_service(
    s3service: S3Service = Depends(get_s3_service),
    image_repository: ImageRepository = Depends(get_image_repository),
    user_repository: UserRepository = Depends(get_user_repository)
) -> ImageService:
    return ImageService(
        s3service=s3service,
        image_repository=image_repository,
        user_repository=user_repository,
    )


async def get_current_payload(
    request: Request,
    authx_service: AuthXService = Depends(get_authx_service),
) -> TokenPayload:
    return await authx_service.secure.access_token_required(request)


async def get_session(
        database: DataBaseConfig = Depends(get_data_base_service),
) -> AsyncGenerator[AsyncSession, None]:
    async with database.async_session() as session:
        yield session
