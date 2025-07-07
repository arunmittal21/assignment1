import asyncio
import logging
import os
import sys
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.donor_models import Donation, Donor
from app.db.session import Base, asyncSessionLocal, engine

logger = logging.getLogger(__name__)


async def init_db():
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema created.")


async def seed_data():
    logger.info("Seeding database with initial data...")
    async with asyncSessionLocal() as db:
        from sqlalchemy import text

        await db.execute(text("DELETE FROM donations"))
        await db.execute(text("DELETE FROM donors"))
        await db.commit()
        logger.debug("Cleared existing donor and donation data.")

        donor1 = Donor(
            name="Alice", blood_group="A+", age=29, last_donated=date(2023, 9, 10)
        )
        donor2 = Donor(name="Bob", blood_group="O-", age=35, last_donated=None)

        donation1 = Donation(
            date=date(2023, 9, 10), volume_ml=500, location="Center A", donor=donor1
        )
        donation2 = Donation(
            date=date(2024, 3, 15), volume_ml=450, location="Clinic B", donor=donor1
        )

        db.add_all([donor1, donor2, donation1, donation2])
        await db.commit()
        logger.info("Seed data inserted successfully.")


if __name__ == "__main__":
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        asyncio.run(init_db())
        asyncio.run(seed_data())
        logger.info("Database initialized and seeded.")
    except Exception as e:
        logger.exception("Failed during DB initialization or seeding")
        import sys

        print(f"DB setup failed: {e}", file=sys.stderr)
