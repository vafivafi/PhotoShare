from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.session import DataBaseConfig
from src.infrastructure.secure.hash_service import ArgonService
from src.infrastructure.cloud_storage.s3_service import S3Service
from src.infrastructure.secure.authx_service import AuthXService, BearerAuthXService
from src.infrastructure.db.repository.image_repository import ImageRepository
from src.infrastructure.db.repository.user_repositoty import UserRepository
from src.service.user_service import UserService

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

@lru_cache(maxsize=1)
def get_bearer_authx_service() -> BearerAuthXService:
    return BearerAuthXService()


def get_image_repository() -> ImageRepository:
    return ImageRepository()

def get_user_repository() -> UserRepository:
    return UserRepository()

def get_user_service(
        user_repository: UserRepository = Depends(get_user_repository),
        password_service: ArgonService = Depends(get_argon_service),
        authx_service: AuthXService = Depends(get_authx_service),
        s3service: S3Service = Depends(get_s3_service),
) -> UserService:
    return UserService(
        user_repository=user_repository,
        password_service=password_service,
        auth_service=authx_service,
        s3_service=s3service,
    )

async def get_session(
        database: DataBaseConfig = Depends(get_data_base_service),
) -> AsyncGenerator[AsyncSession, None]:
    async with database.async_session() as session:
        yield session
