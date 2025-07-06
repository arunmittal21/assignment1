from app.core import app_settings
from app.core.log_config import setup_logging

setup_logging(app_settings.log_level)

import logging

logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.routes.donor_routes import router as donor_router
from app.api.v1.routes.health_route import router as health_router
from app.core.coorelation import CorrelationIdMiddleware
from app.core.exception_handler import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.otel_setup import configure_otel
from app.db.session import engine

try:
    app = FastAPI()

    # # Set CORS
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=["*"],  # dont leave it as *
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_middleware(CorrelationIdMiddleware)

    configure_otel(app, engine)

    # Register routes
    app.include_router(donor_router, prefix=app_settings.api_prefix)
    app.include_router(health_router)  # keep it unversioned and unauthenticated

except Exception as e:
    logger.exception("FastAPI application failed to initialize")
    raise
