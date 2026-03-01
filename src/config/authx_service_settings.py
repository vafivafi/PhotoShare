from functools import lru_cache
from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field

class AuthxServiceSettings(BaseSettings):
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(alias="JWT_ALGORITHM")
    jwt_access_token_expires: int = Field(alias="JWT_ACCESS_TOKEN_EXPIRES")

    model_config = SettingsConfigDict(
        env_file="src/env/authx_service_settings.env",
        env_file_encoding="utf-8",
    )

@lru_cache(maxsize=1)
def get_authx_service_settings() -> AuthxServiceSettings:
    return AuthxServiceSettings()