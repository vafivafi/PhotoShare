from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.infrastructure.log.logger import logger
from src.infrastructure.db.session import DataBaseConfig
from src.presentation.api.routers.user_router import user_router
from src.presentation.api.routers.image_router import image_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    database = DataBaseConfig()
    logger.info("Service is running")

    yield

    await database.disconnect()
    logger.info("Service is stopped")

app = FastAPI(
    lifespan=lifespan,
    title="PhotoShare API",
    version="1.0",
)

app.include_router(user_router)
app.include_router(image_router)
