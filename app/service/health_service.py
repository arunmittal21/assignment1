import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def db_health_check(db: AsyncSession) -> dict:
    logger.info("Pinging database")
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        logger.exception("Failed to query database")
        raise
