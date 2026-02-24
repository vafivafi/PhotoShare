from functools import lru_cache
from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

class CloudStorageSettings(BaseSettings):
    endpoint_url: str = Field(alias="ENDPOINT_URL")
    bucket_name: str = Field(alias="BUCKET_NAME")
    access_key: str = Field(alias="ACCESS_KEY")
    secret_key: str = Field(alias="SECRET_KEY")
    verify_ssl: bool = Field(alias="VERIFY_SSL") #для прода True
    public_s3_url: str = Field(alias="PUBLIC_S3_URL")

    model_config = SettingsConfigDict(
        env_file="src/env/s3_settings.env",
        env_file_encoding="utf-8",
    )

@lru_cache(maxsize=1)
def get_cloud_storage() -> CloudStorageSettings:
    return CloudStorageSettings()
