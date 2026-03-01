from typing import  Optional

from authx import AuthX, AuthXConfig
from fastapi.security import HTTPBearer

from src.config.authx_service_settings import get_authx_service_settings
from src.infrastructure.log.logger import logger

class AuthXService:
    def __init__(self):
        self._settings = get_authx_service_settings()

        self._config: Optional[AuthXConfig] = None
        self._secure: Optional[AuthX] = None

    @property
    def config(self) -> AuthXConfig:
        if self._config is None:
            try:
                self._config = AuthXConfig(
                    JWT_SECRET_KEY=self._settings.jwt_secret_key,
                    JWT_ALGORITHM=self._settings.jwt_algorithm,
                    JWT_ACCESS_TOKEN_EXPIRES=self._settings.jwt_access_token_expires,
                    JWT_TOKEN_LOCATION=['headers']
                )
                logger.info(f"AuthXService config: {self._config}")
            except Exception as e:
                logger.error(f"Failed to initialize AuthXConfig: {e}")
                raise

        return self._config

    @property
    def secure(self) -> AuthX:
        if self._secure is None:
            try:
                self._secure = AuthX(config=self.config)
                logger.info(f"AuthXService secure: {self._secure}")
            except Exception as e:
                logger.error(f"Failed to initialize AuthX: {e}")
                raise

        return self._secure

class BearerAuthXService:
    def __init__(self):
        self._bearer_scheme: Optional[HTTPBearer] = None

    @property
    def bearer_scheme(self) -> HTTPBearer:
        if self._bearer_scheme is None:
            try:
                self._bearer_scheme = HTTPBearer()
                logger.info(f"BearerService config: {self._bearer_scheme}")
            except Exception as e:
                logger.error(f"Failed to initialize HTTPBearer: {e}")
                raise

        return self._bearer_scheme
