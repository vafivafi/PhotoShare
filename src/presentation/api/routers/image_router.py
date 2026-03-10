import uuid
from authx import TokenPayload
from fastapi import APIRouter, status, UploadFile, File, Depends, Body, Query, Path
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.image_service import ImageService
from src.presentation.schemas.image_schema import ImageAddSchema, ImageUpdateNameSchema, ImageUpdateDescriptionSchema
from src.presentation.api.deps import (
    get_image_service,
    get_session,
    get_current_payload
)

image_router = APIRouter(
    prefix="/images",
    tags=["image"]
)

@image_router.post(
    "",
    summary="Create a new photo",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(HTTPBearer())]
)
async def add_photo(
    session: AsyncSession = Depends(get_session),
    image_service: ImageService = Depends(get_image_service),
    payload: TokenPayload = Depends(get_current_payload),
    image: ImageAddSchema = Depends(ImageAddSchema.as_form),
    file: UploadFile = File(...),
):
    return await image_service.upload_file(
        session=session,
        file=file,
        payload=payload,
        image_name=image.name,
        image_description=image.description,
    )

@image_router.get(
    "",
    summary="Get all images",
    status_code=status.HTTP_200_OK,
)
async def get_images(
    session: AsyncSession = Depends(get_session),
    image_service: ImageService = Depends(get_image_service),
    limit: int = Query(
        50,
        ge=1,
        le=100
    ),
    offset: int = Query(
        0,
        ge=0
    )
):
    return await image_service.get_images(
        session=session,
        limit=limit,
        offset=offset,
    )

@image_router.put(
    "/{image_id}/name",
    summary="Update image name",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(HTTPBearer())]
)
async def update_name(
    image_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_session),
    name: ImageUpdateNameSchema = Body(...),
    image_service: ImageService = Depends(get_image_service),
    payload: TokenPayload = Depends(get_current_payload)
):
    return await image_service.update_name(
        session=session,
        image_id=image_id,
        new_name=name.new_name,
        payload=payload
    )

@image_router.put(
    "/{image_id}/description",
    summary="Update image description",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(HTTPBearer())]
)
async def update_description(
    image_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_session),
    description: ImageUpdateDescriptionSchema = Body(...),
    image_service: ImageService = Depends(get_image_service),
    payload: TokenPayload = Depends(get_current_payload)
):
    return await image_service.update_description(
        session=session,
        image_id=image_id,
        new_description=description.new_description,
        payload=payload
    )
