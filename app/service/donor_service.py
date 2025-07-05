from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.schemas import DonationCreate, DonationOut, DonorCreate, DonorOut

# from sqlalchemy.orm import Session
from app.db.models import Donation, Donor


async def create_donor(db: AsyncSession, donor_in: DonorCreate) -> Donor:
    donor = Donor(**donor_in.dict())
    db.add(donor)
    await db.commit()
    await db.refresh(donor)
    return donor


async def get_all_donors(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Donor).offset(skip).limit(limit))
    return result.scalars().all()


async def get_donor(db: AsyncSession, donor_id: int):
    result = await db.execute(select(Donor).filter(Donor.id == donor_id))
    return result.scalar_one_or_none()


async def update_donor(db: AsyncSession, donor_id: int, donor_in: DonorCreate):
    result = await db.execute(select(Donor).filter(Donor.id == donor_id))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    for key, value in donor_in.dict().items():
        setattr(donor, key, value)
    await db.commit()
    await db.refresh(donor)
    return donor


async def delete_donor(db: AsyncSession, donor_id: int):
    result = await db.execute(select(Donor).filter(Donor.id == donor_id))
    donor = result.scalar_one_or_none()
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    # Check if the donor has any donations
    if donor.donations:
        raise HTTPException(
            status_code=400, detail="Cannot delete donor with existing donations"
        )
    # Delete the donor
    await db.commit()
    await db.refresh(donor)
    return {"detail": "Donor deleted successfully"}


async def create_donation(db: AsyncSession, donor_id: int, donation_in: DonationCreate):
    donation = Donation(**donation_in.dict(), donor_id=donor_id)
    db.add(donation)
    await db.commit()
    await db.refresh(donation)
    return donation


# def get_donations_by_donor(db: Session, donor_id: int):
#     return db.query(Donation).filter(Donation.donor_id == donor_id).all()


async def update_donation(
    db: AsyncSession, donation_id: int, donation_in: DonationCreate
):
    result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = result.scalar_one_or_none()

    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")

    for key, value in donation_in.dict().items():
        setattr(donation, key, value)

    await db.commit()
    await db.refresh(donation)
    return donation


async def delete_donation(db: AsyncSession, donation_id: int):
    result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = result.scalar_one_or_none()

    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")

    await db.delete(donation)
    await db.commit()
    return {"detail": "Donation deleted successfully"}
