from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class ArgonSettings(BaseSettings):
    argon_time_cost: int = Field(alias="ARGON_TIME_COST")
    argon_memory_cost: int = Field(alias="ARGON_MEMORY_COST")
    argon_parallelism: int = Field(alias="ARGON_PARALLELISM")
    argon_hash_length: int = Field(alias="ARGON_HASH_LENGTH")
    argon_salt_length: int = Field(alias="ARGON_SALT_LENGTH")

    model_config = SettingsConfigDict(
        env_file="src/env/argon_settings.env",
        env_file_encoding="utf-8",
    )

@lru_cache(maxsize=1)
def get_argon_settings() -> ArgonSettings:
    return ArgonSettings()
