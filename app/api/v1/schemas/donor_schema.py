import datetime
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, constr

VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}


class DonorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    blood_group: str = Field(
        ..., description="Blood group must be one of the standard types"
    )
    age: int = Field(..., ge=18, le=65)
    last_donated: Optional[date] = None

    @classmethod
    def validate_blood_group(cls, values):
        if values.get("blood_group") not in VALID_BLOOD_GROUPS:
            raise ValueError("Invalid blood group")
        return values


class DonorCreate(DonorBase):
    pass


class DonorOut(DonorBase):
    id: int

    class Config:
        orm_mode = True


class DonationBase(BaseModel):
    date: datetime.date = Field(..., description="Date of donation")
    volume_ml: int = Field(..., ge=250, le=600, description="Volume in milliliters")
    location: str = Field(..., min_length=2, max_length=100)
    # add pulse, bloodpressure, hemoglobin, and other fields
    hemoglobin: Optional[float] = Field(
        None, ge=12.0, le=20.0, description="Hemoglobin level in g/dL"
    )
    pulse: Optional[int] = Field(
        None, ge=60, le=100, description="Pulse rate in beats per minute"
    )
    blood_pressure: Optional[str] = Field(
        None,
        description="Blood pressure in format 'systolic/diastolic' (e.g., '120/80')",
    )  # regex=r"^\d{2,3}/\d{2,3}$"
    # Foreign key to Donor
    donor_id: int = Field(..., description="ID of the donor who made the donation")


class DonationCreate(DonationBase):
    pass


class DonationOut(DonationBase):
    id: int

    class Config:
        orm_mode = True
