import logging
import sys

from app.core.async_context import request_id_var


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get() or "-"
        return True


def setup_logging(level: str = "INFO"):
    log_format = (
        "%(asctime)s [%(levelname)s] %(name)s [request_id=%(request_id)s]: %(message)s"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format))
    handler.addFilter(RequestIdFilter())

    logging.basicConfig(level=level.upper(), handlers=[handler])

    # Optional: silence overly verbose loggers from dependencies
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
