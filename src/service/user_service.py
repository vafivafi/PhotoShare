from argon2 import PasswordHasher
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.infrastructure.secure.hash_service import ArgonService
from src.infrastructure.secure.authx_service import AuthXService
from src.infrastructure.cloud_storage.s3_service import S3Service
from src.presentation.schemas.user_schema import UserSchema
from src.infrastructure.log.logger import logger
from src.infrastructure.db.repository.user_repositoty import UserRepository


class UserService:
    def __init__(
            self,
            user_repository: UserRepository,
            password_service: ArgonService,
            auth_service: AuthXService,
            s3_service: S3Service,
    ) -> None:
        self._password_service: ArgonService = password_service
        self._auth_service: AuthXService = auth_service
        self._s3_service: S3Service = s3_service
        self._user_repository: UserRepository = user_repository

    async def create_user(
            self,
            session: AsyncSession,
            user: UserSchema,
    ) -> dict:
        try:
            hashed_password = await self._password_service.hashed_password(
                user.password
            )

            existing_user = await self._user_repository.get_by_username(
                session=session,
                username=user.username,
            )
            if existing_user:
                raise ValueError("User already exists")

            new_user = await self._user_repository.create(
                session=session,
                username=user.username,
                hashed_password=hashed_password,
            )

            await session.commit()
            await session.refresh(new_user)

            token = self._auth_service.secure.create_access_token(str(new_user.id))
            logger.info(f"New user created: {new_user.username}")

            return {
                "message": "User created successfully",
                "user_id": new_user.id,
                "username": new_user.username,
                "created_at": new_user.created_at,
                "token": token,
            }


        except ValueError as e:
            logger.exception("user already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

        except SQLAlchemyError:
            await session.rollback()
            logger.exception("SQLAlchemyError")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error when logging into your account",
            )
        except Exception:
            await session.rollback()
            logger.exception("Exception")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error when logging into your account",
            )
