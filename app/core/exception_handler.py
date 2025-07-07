import json
import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error. Please try again later.",
            # No "errors" field, since it's a generic error
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    logger.warning(f"HTTPException: {exc.detail} at {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail if exc.detail else "HTTP error occurred",
            # Optionally include "errors": [] for more info
        },
    )


def make_serializable_errors(errors):
    try:
        # This will fail if errors isn't serializable
        json.dumps(errors)
        return errors
    except Exception:
        # Fallback: convert all to string
        return [str(e) for e in errors]


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.exception(f"Validation error at {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": make_serializable_errors(exc.errors()),
        },
    )
