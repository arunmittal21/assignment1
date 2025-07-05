import logging
import sys


def setup_logging(level: str = "INFO"):
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logging.basicConfig(
        level=level.upper(),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Optional: silence overly verbose loggers from dependencies
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
