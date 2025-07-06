import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.service import db_health_check

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db_health_check(db)
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Database connection error")
