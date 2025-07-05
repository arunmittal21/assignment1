from app.core import app_settings
from app.core.log_config import setup_logging

setup_logging(app_settings.log_level)

import logging

logger = logging.getLogger(__name__)

from fastapi import FastAPI

from app.api.v1.routes.donor_routes import router as donor_router

app = FastAPI()

app.include_router(donor_router, prefix=app_settings.api_prefix)
