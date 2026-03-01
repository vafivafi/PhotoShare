from contextlib import asynccontextmanager
import uuid
from aiobotocore.session import get_session
from botocore.config import Config
from fastapi import UploadFile

from src.config.s3_service_settings import get_cloud_storage
from src.infrastructure.log.logger import logger

class S3Service:
    def __init__(self):
        _settings = get_cloud_storage()

        self._config = {
            "endpoint_url": _settings.endpoint_url,
            "aws_access_key_id": _settings.access_key,
            "aws_secret_access_key": _settings.secret_key,
            "verify": _settings.verify_ssl
        }
        self._bucket_name = _settings.bucket_name
        self._public_url = _settings.public_s3_url
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

            file_size = len(file_content)
            object_key = f"{uuid.uuid4()}_{file.filename}"
            file_url = f"{self._public_url}/{object_key}"

            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self._bucket_name,
                    Key=object_key,
                    Body=file_content
                )
            logger.info(f"Uploaded file: {file_url}")

            return file_url, file_size
        except Exception as e:
            logger.error(e)
            raise
        finally:
            await file.close()
