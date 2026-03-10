import uuid
from authx import TokenPayload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException, status

from src.infrastructure.cloud_storage.s3_service import S3Service
from src.infrastructure.db.repository.image_repository import ImageRepository
from src.infrastructure.db.repository.user_repositoty import UserRepository
from src.infrastructure.log.logger import logger

class ImageService:
    def __init__(
        self,
        s3service: S3Service,
        image_repository: ImageRepository,
        user_repository: UserRepository
    ) -> None:
        self._s3service: S3Service = s3service
        self._image_repository = image_repository
        self._user_repository = user_repository

    async def upload_file(
        self,
        session: AsyncSession,
        file: UploadFile,
        payload: TokenPayload,
        image_name: str,
        image_description: str
    ) -> dict:
        try:
            user_id = uuid.UUID(payload.sub)
            
            max_size = 5 * 1024 * 1024  #5 MB
            file_content = await file.read()
            file_size = len(file_content)

            if file_size > max_size:
                logger.error(f"File size {file_size} exceeds maximum allowed size of {max_size} bytes")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size {file_size} exceeds maximum allowed size of {max_size} bytes"
                )

            allowed_extensions = (".jpg", ".jpeg", ".png", ".webp")
            filename = file.filename
            if not filename or not filename.lower().endswith(allowed_extensions):
                logger.error(f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}"
                )
            
            await file.seek(0)

            user = await self._user_repository.get_by_id(
                session=session,
                user_id=user_id,
            )

            if user is None:
                logger.error(f"User not found: user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            image_url, image_size = await self._s3service.upload_file(
                file=file
            )
            
            image = await self._image_repository.create_image(
                session=session,
                user_id=user_id,
                image_size=image_size,
                image_url=image_url,
                name=image_name,
                description=image_description
            )

            logger.info(f"Image: {image.name} added")

            await session.commit()
            await session.refresh(image)

            return {
                "message": "Image successfully added",
                "user_id": user_id,
                "image_id": image.id,
                "image_description": image.description,
                "image_name": image.name,
                "image_size": image.image_size,
                "image_url": image.image_url,
            }

        except HTTPException:
            raise
        except ValueError as exc:
            logger.error(f"Invalid UUID in payload.sub: {payload.sub}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.exception(f"Database error in create image: {image_name}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error in create image: {image_name}"
            )
        except Exception as exc:
            await session.rollback()
            logger.exception(f"Unknown error in create image: {image_name}", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unknown error in create image: {image_name}"
            )

    async def get_images(
        self,
        session: AsyncSession,
        limit: int,
        offset: int,
    ) -> dict:
        try:
            images = await self._image_repository.get_images(
                session=session,
                limit=limit,
                offset=offset,
            )

            if not images:
                logger.info("images not found")
                return {
                    "message": "images not found"
                }
            
            logger.info("images found")
            return {
                "message": "images found",
                "images": [
                    {
                        "image_id": image.id,
                        "image_user_id": image.user_id,
                        "image_size": image.image_size,
                        "image_url": image.image_url,
                        "image_name": image.name,
                        "image_description": image.description,
                        "image_created_at": image.created_at,
                        "user_name": image.user.username
                    }
                for image in images]
            }

        except SQLAlchemyError as exc:
            logger.exception(f"Database error in get images", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {exc}"
            )
        except Exception as exc:
            logger.exception(f"Unknown error in get images", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unknown error in get images: {exc}"
            )
    
    async def get_user_images(
        self,
        session: AsyncSession,
        payload: TokenPayload,
    ) -> dict:
        try:    
            user_id = uuid.UUID(payload.sub)

            images = await self._image_repository.get_images_user_id(
                session=session,
                user_id=user_id
            )
            
            if not images:
                logger.info(f"Images not found, id: {user_id}")
                return {
                    "message": "Images not found"
                }
            
            logger.info("Images found")
            return {
                "message": "Images found",
                "images": [
                    {
                            "image_id": image.id,
                            "image_user_id": image.user_id,
                            "image_size": image.image_size,
                            "image_url": image.image_url,
                            "image_name": image.name,
                            "image_description": image.description,
                            "image_created_at": image.created_at,
                            "user_name": image.user.username
                    }
                for image in images]
            }

        except ValueError as exc:
            logger.error(f"Invalid UUID in payload.sub: {payload.sub}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        except SQLAlchemyError as exc:
            logger.exception("Database error in get_user_images", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error in get_user_images"
            )
        except Exception as exc:
            logger.exception("Unknown error in get_user_images", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error in get_user_images"
            )

    async def update_description(
        self,
        new_description: str,
        session: AsyncSession,
        payload: TokenPayload,
        image_id: uuid.UUID,
    ) -> dict:
        try:
            user_id = uuid.UUID(payload.sub)

            image = await self._image_repository.update_description(
                session=session,
                image_id=image_id,
                user_id=user_id,
                new_description=new_description,
            )
            if not image:
                logger.error(f"Image {image_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="image not found",
                )

            await session.commit()
            await session.refresh(image)

            logger.info(f"Image {image_id} description updated")

            return {
                "message": "Description updated",
                "image_id": image.id,
                "image_description": image.description,
            }

        except ValueError as exc:
            logger.error(f"Invalid UUID in payload.sub: {payload.sub}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.exception("Database error in update_description", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error in update_description"
            )
        except Exception as exc:
            await session.rollback()
            logger.exception("Unknown error in update_description", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error in update_description"
            )
    
    async def update_name(
        self,
        session: AsyncSession,
        payload: TokenPayload,
        image_id: uuid.UUID,
        new_name: str,
    ) -> dict:
        try:
            user_id = uuid.UUID(payload.sub)

            image = await self._image_repository.update_name(
                session=session,
                image_id=image_id,
                user_id=user_id,
                new_name=new_name,
            )
            if not image:
                logger.error(f"Image {image_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="image not found"
                )

            await session.commit()
            await session.refresh(image)

            logger.info(f"Image {image_id} name updated")

            return {
                "message": "Name updated",
                "image_id": image.id,
                "image_name": image.name,
            }

        except ValueError as exc:
            logger.error(f"Invalid UUID in payload.sub: {payload.sub}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.exception("Database error in update_name", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error in update_name"
            )
        except Exception as exc:
            await session.rollback()
            logger.exception("Unknown error in update_name", exc_info=exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unknown error in update_name"
            )
