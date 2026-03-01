from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine


from src.config.database_settings import get_database_settings
from src.infrastructure.log.logger import logger

class DataBaseConfig:
    def __init__(self):
        self._db_url = get_database_settings().database_url
        self._async_engine: Optional[AsyncEngine] = None
        self._async_session: Optional[async_sessionmaker[AsyncSession]] = None

    @property
    def async_engine(self) -> AsyncEngine:
        try:
            if self._async_engine is None:
                self._async_engine = create_async_engine(self._db_url)
            return self._async_engine
        except SQLAlchemyError:
            logger.exception("Database connection failed")
            raise

    @property
    def async_session(self) -> async_sessionmaker[AsyncSession]:
        try:
            if self._async_session is None:
                self._async_session = async_sessionmaker(
                    expire_on_commit=False,
                    bind=self.async_engine,
                )
            return self._async_session
        except SQLAlchemyError:
            logger.exception("Database connection failed")
            raise

    async def disconnect(self):
        try:
            await self.async_engine.dispose()
            logger.info("Database disconnected")
        except SQLAlchemyError:
            logger.exception("Database connection failed")
            raise
