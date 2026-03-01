from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.session import DataBaseConfig
from src.infrastructure.secure.hash_service import ArgonService
from src.infrastructure.cloud_storage.s3_service import S3Service
from src.infrastructure.secure.authx_service import AuthXService, BearerAuthXService

@lru_cache(maxsize=1)
def get_argon_service() -> ArgonService:
    return ArgonService()

@lru_cache(maxsize=1)
def get_s3_service() -> S3Service:
    return S3Service()

@lru_cache(maxsize=1)
def get_data_service() -> DataBaseConfig:
    return DataBaseConfig()

@lru_cache(maxsize=1)
def get_authx_service() -> AuthXService:
    return AuthXService()

@lru_cache(maxsize=1)
def get_bearer_authx_service() -> BearerAuthXService:
    return BearerAuthXService()

async def get_session(
        database: DataBaseConfig = Depends(get_data_service),
) -> AsyncGenerator[AsyncSession, None]:
    async with database.async_session() as session:
        yield session
