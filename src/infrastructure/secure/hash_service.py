from typing import Optional
import asyncio
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.config.argon_service_settings import ArgonSettings
from src.infrastructure.log.logger import logger

class ArgonService:
    def __init__(self):
        self._settings = ArgonSettings()
        self._password_hasher: Optional[PasswordHasher] = None

    @property
    def password_hasher(self):
        if self._password_hasher is None:
            self._password_hasher = PasswordHasher(
                self._settings.argon_time_cost,
                self._settings.argon_memory_cost,
                self._settings.argon_parallelism,
                self._settings.argon_hash_length,
                self._settings.argon_salt_length
            )
        return self._password_hasher

    async def hashed_password(self, password: str) -> str:
        return await asyncio.to_thread(
            self.password_hasher.hash,
            password
        )
    async def verify_password(self, hashed_password: str, password: str) -> bool:
        try:
            return await asyncio.to_thread(
                self.password_hasher.verify,
                hashed_password,
                password

            )
        except VerifyMismatchError:
            logger.info(
                "Password verification failed. Password is incorrect."
            )
            return False
