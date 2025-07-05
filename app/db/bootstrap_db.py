import asyncio
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.donor_models import Donation, Donor
from app.db.session import Base, asyncSessionLocal, engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_data():
    async with asyncSessionLocal() as db:
        from sqlalchemy import text

        await db.execute(text("DELETE FROM donations"))
        await db.execute(text("DELETE FROM donors"))
        await db.commit()

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


if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(seed_data())


# from datetime import date
# from sqlalchemy.orm import Session

# from app.db.session import engine, Base, SessionLocal
# from app.db.models.donor_models import Donor, Donation

# # --- Create tables ---
# def init_db():
#     Base.metadata.create_all(bind=engine)

# # --- Add sample data ---
# def seed_data():
#     db: Session = SessionLocal()

#     # Clear existing records for a clean slate (optional)
#     db.query(Donation).delete()
#     db.query(Donor).delete()
#     db.commit()

#     # Sample donors
#     donor1 = Donor(
#         name="Alice Johnson",
#         blood_group="A+",
#         age=29,
#         last_donated=date(2023, 9, 10)
#     )

#     donor2 = Donor(
#         name="Bob Smith",
#         blood_group="O-",
#         age=35,
#         last_donated=None
#     )

#     # Sample donations
#     donation1 = Donation(
#         date=date(2023, 9, 10),
#         volume_ml=500,
#         location="Red Cross Center",
#         hemoglobin=13.5,
#         pulse=72,
#         blood_pressure="120/80",
#         donor=donor1
#     )

#     donation2 = Donation(
#         date=date(2024, 3, 15),
#         volume_ml=450,
#         location="Downtown Clinic",
#         hemoglobin=14.2,
#         pulse=76,
#         blood_pressure="118/78",
#         donor=donor1
#     )

#     db.add_all([donor1, donor2, donation1, donation2])
#     db.commit()
#     db.close()

# # --- Entrypoint ---
# if __name__ == "__main__":
#     init_db()
#     seed_data()
#     print("✅ Database initialized and seeded with sample data.")
