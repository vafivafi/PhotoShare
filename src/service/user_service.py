import uuid
from authx import TokenPayload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.infrastructure.secure.hash_service import ArgonService
from src.infrastructure.secure.authx_service import AuthXService
from src.presentation.schemas.user_schema import UserSchema, UpdateUsernameSchema
from src.infrastructure.log.logger import logger
from src.infrastructure.db.repository.user_repositoty import UserRepository


class UserService:
    def __init__(
            self,
            user_repository: UserRepository,
            password_service: ArgonService,
            auth_service: AuthXService,
    ) -> None:
        self._password_service: ArgonService = password_service
        self._auth_service: AuthXService = auth_service
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
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already exists",
                )

            new_user = await self._user_repository.create(
                session=session,
                username=user.username,
                hashed_password=hashed_password,
            )

            await session.commit()
            await session.refresh(new_user)

            token = self._auth_service.secure.create_access_token(str(new_user.id))
            logger.info(f"User created: username={new_user.username}, user_id={new_user.id}")

            return {
                "message": "User created successfully",
                "user_id": new_user.id,
                "username": new_user.username,
                "created_at": new_user.created_at,
                "token": token,
            }


        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.exception(f"Database error in create_user: username={user.username}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while registering an account",
            )
        except Exception as exc:
            await session.rollback()
            logger.exception(f"Unexpected error in create_user: username={user.username}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error while registering an account",
            )

    async def login(
            self,
            session: AsyncSession,
            user: UserSchema,
    ) -> dict:
        try:
            existing_user = await self._user_repository.get_by_username(
                session=session,
                username=user.username,
            )
            if existing_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                )

            if await self._password_service.verify_password(
                existing_user.password,
                user.password,
            ):
                logger.info(f"Login successful: username={existing_user.username}, user_id={existing_user.id}")
                token = self._auth_service.secure.create_access_token(str(existing_user.id))
                return {
                    "message": "Login successful",
                    "user_id": existing_user.id,
                    "username": existing_user.username,
                    "created_at": existing_user.created_at,
                    "token": token,
                }
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            logger.exception(f"Database error in login: username={user.username}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error when logging into your account",
            )
        except Exception as exc:
            logger.exception(f"Unexpected error in login: username={user.username}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error when logging into your account",
            )

    async def get_user(
            self,
            session: AsyncSession,
            username: str,
    ) -> dict:
        try:
            user = await self._user_repository.get_by_username(
                session=session,
                username=username,
            )
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )
            logger.info(f"User found: username={username}, user_id={user.id}")
            return {
                "message": "User found",
                "user_id": user.id,
                "username": user.username,
                "created_at": user.created_at,
            }

        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            logger.exception(f"Database error in get_user: username={username}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error when getting user by username",
            )

        except Exception as exc:
            logger.exception(f"Unexpected error in get_user: username={username}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error when getting user by username",
            )

    async def get_by_username_with_images(
            self,
            session: AsyncSession,
            username: str,
    ) -> dict:
        try:
            user = await self._user_repository.get_by_username_with_images(
                session=session,
                username=username,
            )
            if user is None:
                logger.info(f"User not found: username={username}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.info(f"User found: username={username}, user_id={user.id}, images_count={len(user.images)}")
            return {
                "message": "User found",
                "user_id": user.id,
                "username": user.username,
                "created_at": user.created_at,
                "images": [
                    {
                        "id": image.id,
                        "name": image.name,
                        "size": image.image_size,
                        "url": image.image_url,
                        "description": image.description,
                        "created_at": image.created_at,
                    }
                for image in user.images]
            }
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            logger.exception(f"Database error in get_by_username_with_images: username={username}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error when getting user with images",
            )
        except Exception as exc:
            logger.exception(f"Unexpected error in get_by_username_with_images: username={username}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error when getting user with images",
            )

    async def update_username(
        self,
        session: AsyncSession,
        username: UpdateUsernameSchema,
        payload: TokenPayload,
    ) -> dict:

        try:
            user_id = uuid.UUID(payload.sub)

            user = await self._user_repository.get_by_id(
                user_id=user_id,
                session=session
            )
            if user is None:
                logger.error(f"User not found: user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            if user.username == username.new_username:
                logger.info(f"Username not updated: user_id={user_id}, username={user.username}")
                return {
                    "message": "The usernames are the same",
                    "username": user.username,
                    "changed": False
                }

            user = await self._user_repository.get_by_username(
                session=session,
                username=username.new_username,
            )

            if user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="username is taken"
                )

            user = await self._user_repository.update_username(
                session=session,
                user_id=user_id,
                new_username=username.new_username,
            )


            logger.info(f"Username updated: user_id={user_id}, new_username={username.new_username}")
            await session.commit()
            await session.refresh(user)

            return {
                "message": "Username updated successfully",
                "user_id": user.id,
                "username": user.username,
                "created_at": user.created_at,
                "changed": True,
            }

        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.exception("Database error updating username", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while updating username"
            )
        except Exception as exc:
            await session.rollback()
            logger.exception("Unknown error updating username", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error while updating username"
            )

    async def profile(
        self,
        session: AsyncSession,
        payload: TokenPayload
    ) -> dict:
        try:
            user_id = uuid.UUID(payload.sub)

            user = await self._user_repository.get_by_id(
                user_id=user_id,
                session=session,
            )
            
            if user is None:
                logger.error(f"User not found: user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            logger.info(f"Profile found: user_id={user_id}, username={user.username}")

            return {
                "message": "Profile found",
                "user_id": user.id,
                "username": user.username,
                "created_at": user.created_at,
                "images": [
                    {
                        "id": image.id,
                        "name": image.name,
                        "size": image.image_size,
                        "url": image.image_url,
                        "description": image.description,
                        "created_at": image.created_at,
                    }
                for image in user.images]
            }

        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            logger.exception("Database error when find user profile", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error when find user profile",
            )
        except Exception as exc:
            logger.exception("Unknown error when find user profile", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error when find user profile",
            )
