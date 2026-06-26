from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler, unhandled_exception_handler
from app.core.logging import configure_logging
from app.db.init_db import create_database_tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Ensure tables exist on startup so the app runs out of the box (e.g. in
    # Docker) without a separate migration step.
    await create_database_tables()
    yield


def create_app() -> FastAPI:
    configure_logging()

    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
        version=settings.APP_VERSION,
        description="Healthcare assistant API with chat, document upload, and RAG analysis.",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(AppException, app_exception_handler)
    application.add_exception_handler(Exception, unhandled_exception_handler)
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return application


app = create_app()

