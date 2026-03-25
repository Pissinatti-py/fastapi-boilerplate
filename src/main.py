from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.endpoints.auth import auth_router
from src.api.v1.router import api_router
from src.core.settings import settings
from src.middlewares.rate_limit_middleware import RateLimitMiddleware
from src.services.logger_service import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifecycle.

    This function is called when the application starts and stops.
    It runs database migrations synchronously in a background thread
    at startup and handles cleanup operations on shutdown.

    :param app: The FastAPI application instance.
    :type app: FastAPI

    :yield: Control back to the application runtime
    after startup tasks are completed.
    :rtype: None
    """
    logger.info("🚀 Application is starting...")

    yield

    logger.warning("🛑 Application is shutting down...")


def get_application() -> FastAPI:
    """
    Creates and configures the FastAPI application instance.

    This function sets up:
    - The application title and version.
    - OpenAPI documentation routes.
    - CORS middleware with allowed origins.
    - API routes with the configured prefix.
    - Lifespan event handling (startup and shutdown hooks).

    :return: Configured FastAPI application instance.
    :rtype: FastAPI
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate Limit
    app.add_middleware(
        RateLimitMiddleware,
        redis_url=settings.REDIS_URL,
        max_requests=settings.RATE_LIMIT_MAX_REQUESTS,
        window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    )

    # Include API routes
    app.include_router(api_router, prefix=settings.API_PREFIX)
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

    return app


app = get_application()
