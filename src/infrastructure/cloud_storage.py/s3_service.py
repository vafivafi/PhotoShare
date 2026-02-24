from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from botocore.config import Config
from fastapi import UploadFile

from src.config.s3_service_settings import get_cloud_storage
from src.infrastructure.log.logger import logger

class S3Service:
    def __init__(self):
        settings = get_cloud_storage()

        self._config = {
            "endpoint_url": settings.endpoint_url,
            "aws_access_key_id": settings.access_key,
            "aws_secret_access_key": settings.secret_key,
            "verify": settings.verify_ssl
        }
        self._bucket_name = settings.bucket_name
        self._public_url = settings.public_s3_url
        self._session = get_session()

    @asynccontextmanager
    async def get_client(self):
        botocore_config = Config(
            request_checksum_calculation="when_required"
        )
        async with self._session.create_client(
            "s3",
            config=botocore_config,
            **self._config
        ) as client:
            yield client

    async def upload_file(self, file: UploadFile):
        try:
            file_content = await file.read()

            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self._bucket_name,
                    Key=file.filename,
                    Body=file_content
                )
            file_url = f"{self._public_url}/{file.filename}"
            logger.info(f"Uploaded file: {file_url}")

            return file_url
        finally:
            await file.close()
