import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.schemas import DonationCreate, DonorCreate
from app.db.models import Donation, Donor

logger = logging.getLogger(__name__)


async def create_donor(db: AsyncSession, donor_in: DonorCreate) -> Donor:
    logger.info(f"Creating donor: {donor_in.name}")
    try:
        donor = Donor(**donor_in.model_dump())
        db.add(donor)
        await db.commit()
        await db.refresh(donor)
        logger.debug(f"Donor created with ID: {donor.id}")
        return donor
    except Exception as e:
        logger.exception("Failed to create donor")
        raise


async def get_all_donors(db: AsyncSession, skip: int = 0, limit: int = 100):
    logger.info(f"Fetching all donors (skip={skip}, limit={limit})")
    try:
        result = await db.execute(select(Donor).offset(skip).limit(limit))
        donors = result.scalars().all()
        logger.debug(f"Retrieved {len(donors)} donors")
        return donors
    except Exception as e:
        logger.exception("Failed to fetch donors")
        raise


async def get_donor(db: AsyncSession, donor_id: int):
    logger.info(f"Fetching donor ID: {donor_id}")
    try:
        result = await db.execute(select(Donor).filter(Donor.id == donor_id))
        donor = result.scalar_one_or_none()
        if donor:
            logger.debug(f"Found donor: {donor.id}")
        else:
            logger.warning(f"Donor with ID {donor_id} not found")
        return donor
    except Exception as e:
        logger.exception(f"Failed to fetch donor ID: {donor_id}")
        raise


async def update_donor(db: AsyncSession, donor_id: int, donor_in: DonorCreate):
    logger.info(f"Updating donor ID: {donor_id}")
    try:
        result = await db.execute(select(Donor).filter(Donor.id == donor_id))
        donor = result.scalar_one_or_none()
        if donor is None:
            logger.warning(f"Donor with ID {donor_id} not found for update")
            raise HTTPException(status_code=404, detail="Donor not found")

        for key, value in donor_in.model_dump().items():
            setattr(donor, key, value)
        await db.commit()
        await db.refresh(donor)
        logger.debug(f"Updated donor ID: {donor_id}")
        return donor
    except Exception as e:
        logger.exception(f"Failed to update donor ID: {donor_id}")
        raise


async def delete_donor(db: AsyncSession, donor_id: int):
    logger.info(f"Deleting donor ID: {donor_id}")
    try:
        result = await db.execute(select(Donor).filter(Donor.id == donor_id))
        donor = result.scalar_one_or_none()
        if donor is None:
            logger.warning(f"Donor with ID {donor_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Donor not found")
        if donor.donations:
            logger.warning(f"Cannot delete donor ID {donor_id}: has donations")
            raise HTTPException(
                status_code=400, detail="Cannot delete donor with existing donations"
            )

        await db.delete(donor)
        await db.commit()
        logger.info(f"Deleted donor ID: {donor_id}")
        return {"detail": "Donor deleted successfully"}
    except Exception as e:
        logger.exception(f"Failed to delete donor ID: {donor_id}")
        raise


async def create_donation(db: AsyncSession, donor_id: int, donation_in: DonationCreate):
    logger.info(f"Creating donation for donor ID: {donor_id}")
    try:

        data = donation_in.model_dump()
        data.pop("donor_id", None)
        donation = Donation(**data, donor_id=donor_id)
        # donation = Donation(**donation_in.model_dump(), donor_id=donor_id)
        db.add(donation)
        await db.commit()
        await db.refresh(donation)
        logger.debug(f"Donation created with ID: {donation.id}")
        return donation
    except Exception as e:
        logger.exception("Failed to create donation")
        raise


async def update_donation(
    db: AsyncSession, donation_id: int, donation_in: DonationCreate
):
    logger.info(f"Updating donation ID: {donation_id}")
    try:
        result = await db.execute(select(Donation).where(Donation.id == donation_id))
        donation = result.scalar_one_or_none()
        if donation is None:
            logger.warning(f"Donation with ID {donation_id} not found for update")
            raise HTTPException(status_code=404, detail="Donation not found")

        for key, value in donation_in.dict().items():
            setattr(donation, key, value)

        await db.commit()
        await db.refresh(donation)
        logger.debug(f"Updated donation ID: {donation_id}")
        return donation
    except Exception as e:
        logger.exception(f"Failed to update donation ID: {donation_id}")
        raise


async def delete_donation(db: AsyncSession, donation_id: int):
    logger.info(f"Deleting donation ID: {donation_id}")
    try:
        result = await db.execute(select(Donation).where(Donation.id == donation_id))
        donation = result.scalar_one_or_none()
        if donation is None:
            logger.warning(f"Donation with ID {donation_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Donation not found")

        await db.delete(donation)
        await db.commit()
        logger.info(f"Deleted donation ID: {donation_id}")
        return {"detail": "Donation deleted successfully"}
    except Exception as e:
        logger.exception(f"Failed to delete donation ID: {donation_id}")
        raise
