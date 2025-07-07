import logging

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.schemas import DonationCreate, DonationUpdate, DonorCreate, DonorUpdate
from app.db.models import Donation, Donor

logger = logging.getLogger(__name__)


# ========== DONOR  ==========


async def create_donor(db: AsyncSession, donor_in: DonorCreate) -> Donor:
    logger.info(f"Creating donor: {donor_in.name}")
    try:
        donor = Donor(**donor_in.model_dump())
        db.add(donor)
        await db.commit()
        await db.refresh(donor)
        logger.debug(f"Donor created with ID: {donor.id}")
        return donor
    except Exception:
        logger.exception("Failed to create donor")
        raise


async def get_all_donors(db: AsyncSession, skip: int = 0, limit: int = 100):
    logger.info(f"Fetching all donors (skip={skip}, limit={limit})")
    try:
        result = await db.execute(select(Donor).offset(skip).limit(limit))
        donors = result.scalars().all()
        logger.debug(f"Retrieved {len(donors)} donors")
        return donors
    except Exception:
        logger.exception("Failed to fetch donors")
        raise


async def get_donor(
    db: AsyncSession, donor_id: int, raise_error_when_not_found: bool = True
):
    logger.info(f"Fetching donor ID: {donor_id}")
    try:
        result = await db.execute(select(Donor).filter(Donor.id == donor_id))
        donor = result.scalar_one_or_none()
        if donor is None and raise_error_when_not_found:
            logger.warning(f"Donor with ID {donor_id} not found")
            raise HTTPException(status_code=404, detail="Donor not found")
        return donor
    except Exception:
        logger.exception(f"Failed to fetch donor ID: {donor_id}")
        raise


async def update_donor(db: AsyncSession, donor_id: int, donor_in: DonorUpdate):
    logger.info(f"Updating donor ID: {donor_id}")
    try:
        donor = await get_donor(db, donor_id, True)
        for key, value in donor_in.model_dump().items():
            setattr(donor, key, value)
        await db.commit()
        await db.refresh(donor)
        logger.debug(f"Updated donor ID: {donor_id}")
        return donor
    except Exception:
        logger.exception(f"Failed to update donor ID: {donor_id}")
        raise


async def delete_donor(db: AsyncSession, donor_id: int):
    logger.info(f"Deleting donor ID: {donor_id}")
    try:
        donor = await get_donor(db, donor_id, True)
        if donor.donations:  # type: ignore
            logger.warning(f"Cannot delete donor ID {donor_id}: has donations")
            raise HTTPException(
                status_code=400, detail="Cannot delete donor with existing donations"
            )
        await db.delete(donor)
        await db.commit()
        logger.info(f"Deleted donor ID: {donor_id}")
        return {"detail": "Donor deleted successfully"}
    except Exception:
        logger.exception(f"Failed to delete donor ID: {donor_id}")
        raise


async def get_total_donor_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Donor))
    total = result.scalar_one()
    return total


# ========== DONATION  ==========


async def create_donation(db: AsyncSession, donor_id: int, donation_in: DonationCreate):
    logger.info(f"Creating donation for donor ID: {donor_id}")
    try:
        data = donation_in.model_dump()
        data.pop("donor_id", None)
        donation = Donation(**data, donor_id=donor_id)
        db.add(donation)
        await db.commit()
        await db.refresh(donation)
        logger.debug(f"Donation created with ID: {donation.id}")
        return donation
    except Exception:
        logger.exception("Failed to create donation")
        raise


async def get_donation(
    db: AsyncSession, donation_id: int, raise_error_when_not_found: bool = True
):
    logger.info(f"Fetching donation ID: {donation_id}")
    try:
        result = await db.execute(select(Donation).where(Donation.id == donation_id))
        donation = result.scalar_one_or_none()
        if donation is None and raise_error_when_not_found:
            logger.warning(f"Donation with ID {donation_id} not found")
            raise HTTPException(status_code=404, detail="Donation not found")
        return donation
    except Exception:
        logger.exception(f"Failed to fetch donation ID: {donation_id}")
        raise


async def update_donation(
    db: AsyncSession, donation_id: int, donation_in: DonationUpdate
):
    logger.info(f"Updating donation ID: {donation_id}")
    try:
        donation = await get_donation(db, donation_id, True)
        for key, value in donation_in.model_dump().items():
            setattr(donation, key, value)
        await db.commit()
        await db.refresh(donation)
        logger.debug(f"Updated donation ID: {donation_id}")
        return donation
    except Exception:
        logger.exception(f"Failed to update donation ID: {donation_id}")
        raise


async def delete_donation(db: AsyncSession, donation_id: int):
    logger.info(f"Deleting donation ID: {donation_id}")
    try:
        donation = await get_donation(db, donation_id, True)
        await db.delete(donation)
        await db.commit()
        logger.info(f"Deleted donation ID: {donation_id}")
        return {"detail": "Donation deleted successfully"}
    except Exception:
        logger.exception(f"Failed to delete donation ID: {donation_id}")
        raise
