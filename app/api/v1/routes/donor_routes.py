import logging

from fastapi import APIRouter, Depends, HTTPException, Query

# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    DonationCreate,
    DonationOut,
    DonationUpdate,
    DonorCreate,
    DonorOut,
    DonorUpdate,
)
from app.api.v1.schemas.common import PaginatedResponse
from app.db.session import get_db
from app.service import (
    create_donation,
    create_donor,
    delete_donation,
    delete_donor,
    get_all_donors,
    get_donor,
    get_total_donor_count,
    update_donation,
    update_donor,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# --- Donor Routes ---
@router.post("/donors", response_model=DonorOut, tags=["Donors"], status_code=201)
async def create_donor_route(donor: DonorCreate, db: AsyncSession = Depends(get_db)):
    logger.info("POST /donors")
    return await create_donor(db, donor)


@router.get("/donors", response_model=PaginatedResponse[DonorOut], tags=["Donors"])
async def list_donors(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max number of records to return"),
):
    logger.info(f"GET /donors?skip={skip}&limit={limit}")
    donors = await get_all_donors(db, skip=skip, limit=limit)
    total = await get_total_donor_count(db)
    donors_out = [
        DonorOut.model_validate(donor, from_attributes=True) for donor in donors
    ]
    return PaginatedResponse[DonorOut](total=total, items=donors_out)


@router.get("/donors/{donor_id}", response_model=DonorOut, tags=["Donors"])
async def get_donor_by_id(donor_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"GET /donors/{donor_id}")
    donor = await get_donor(db, donor_id)
    if donor is None:
        logger.warning(f"Donor ID {donor_id} not found")
        raise HTTPException(status_code=404, detail="Donor not found")
    return donor


@router.put("/donors/{donor_id}", response_model=DonorOut, tags=["Donors"])
async def update_donor_route(
    donor_id: int, donor: DonorUpdate, db: AsyncSession = Depends(get_db)
):
    return await update_donor(db, donor_id, donor)


@router.delete("/donors/{donor_id}", tags=["Donors"], status_code=204)
async def delete_donor_route(donor_id: int, db: AsyncSession = Depends(get_db)):
    await delete_donor(db, donor_id)
    return None  # 204: No Content


# --- Donation Routes ---
@router.post(
    "/donors/{donor_id}/donations",
    response_model=DonationOut,
    tags=["Donations"],
    status_code=201,
)
async def create_donation_route(
    donor_id: int, donation: DonationCreate, db: AsyncSession = Depends(get_db)
):
    logger.info(f"POST /donors/{donor_id}/donations")
    return await create_donation(db, donor_id, donation)


@router.put("/donations/{donation_id}", response_model=DonationOut, tags=["Donations"])
async def update_donation_route(
    donation_id: int, donation: DonationUpdate, db: AsyncSession = Depends(get_db)
):
    return await update_donation(db, donation_id, donation)


@router.delete("/donations/{donation_id}", tags=["Donations"], status_code=204)
async def delete_donation_route(donation_id: int, db: AsyncSession = Depends(get_db)):
    await delete_donation(db, donation_id)
    return None
