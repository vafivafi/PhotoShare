from functools import lru_cache
from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

class DatabaseSettings(BaseSettings):
    database_url: str = Field(default="aiosqlite:///db.sqlite", alias="DATABASE_URL")

    model_config = SettingsConfigDict(
        env_file="src/env/database_settings.env",
        env_file_encoding="utf-8",
    )

@lru_cache(maxsize=1)
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()
