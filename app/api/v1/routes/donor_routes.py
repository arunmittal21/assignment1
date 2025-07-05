from fastapi import APIRouter, Depends, HTTPException

# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import DonationCreate, DonationOut, DonorCreate, DonorOut
from app.db.session import get_db
from app.service import (
    create_donation,
    create_donor,
    delete_donation,
    delete_donor,
    get_all_donors,
    get_donor,
    update_donation,
    update_donor,
)

router = APIRouter()


# --- Donor Routes ---
@router.post("/donors", response_model=DonorOut, tags=["Donors"])
async def create_donor_route(donor: DonorCreate, db: AsyncSession = Depends(get_db)):
    return await create_donor(db, donor)


@router.get("/donors", response_model=list[DonorOut], tags=["Donors"])
async def list_donors(db: AsyncSession = Depends(get_db)):
    return await get_all_donors(db)


@router.get("/donors/{donor_id}", response_model=DonorOut, tags=["Donors"])
async def get_donor_by_id(donor_id: int, db: AsyncSession = Depends(get_db)):
    donor = await get_donor(db, donor_id)
    if donor is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    return donor


# --- Donation Routes ---
@router.post(
    "/donors/{donor_id}/donations", response_model=DonationOut, tags=["Donations"]
)
async def create_donation_route(
    donor_id: int, donation: DonationCreate, db: AsyncSession = Depends(get_db)
):
    return await create_donation(db, donor_id, donation)
