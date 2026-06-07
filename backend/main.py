from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.auth import router as auth_router
from backend.api.bot import router as bot_router
from backend.api.health import router as health_router
from backend.api.tools import router as tools_router
from backend.core.config import get_settings
from backend.core.db import close_redis
from backend.core.logging import get_logger, setup_logging

logger = get_logger("kairos")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging()
    settings = get_settings()
    logger.info(
        "app_start",
        environment=settings.environment,
        mock_external_apis=settings.mock_external_apis,
    )
    yield
    await close_redis()
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Kairos", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url, "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(tools_router)
    app.include_router(bot_router)
    return app


app = create_app()
