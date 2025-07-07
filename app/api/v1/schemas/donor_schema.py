import datetime
import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, constr, field_validator, model_validator

VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}


class DonorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    blood_group: str = Field(
        ..., description="Blood group must be one of the standard types"
    )
    age: int = Field(..., ge=18, le=70)
    last_donated: Optional[date] = None

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, val):
        if val not in VALID_BLOOD_GROUPS:
            raise ValueError(f"Invalid blood group: {val}")
        return val


class DonorCreate(DonorBase):
    pass


class DonorUpdate(DonorBase):
    updated_at: datetime.datetime


class DonorOut(DonorBase):
    id: int
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


class DonationBase(BaseModel):
    date: datetime.date = Field(..., description="Date of donation")
    volume_ml: int = Field(..., ge=250, le=600, description="Volume in milliliters")
    location: str = Field(..., min_length=2, max_length=100)
    # add pulse, bloodpressure, hemoglobin, and other fields
    hemoglobin: Optional[float] = Field(None, description="Hemoglobin level in g/dL")

    @field_validator("hemoglobin")
    @classmethod
    def validate_hemoglobin(cls, val: Optional[float]) -> Optional[float]:
        if val is not None:
            if val < 12.0 or val > 20.0:
                raise ValueError("Hemoglobin must be between 12.0 and 20.0 g/dL")
        return val

    pulse: Optional[int] = Field(None, description="Pulse rate in beats per minute")

    @field_validator("pulse")
    @classmethod
    def validate_pulse(cls, val: Optional[int]) -> Optional[int]:
        if val is not None:
            if val < 60 or val > 200:
                raise ValueError("Pulse must be between 60 and 200 beats per minute")
        return val

    blood_pressure: Optional[str] = Field(
        None,
        description="Blood pressure in format 'systolic/diastolic' (e.g., '120/80')",
    )  # regex=r"^\d{2,3}/\d{2,3}$"

    @field_validator("blood_pressure")
    @classmethod
    def validate_blood_pressure(cls, val: Optional[str]) -> Optional[str]:
        if val is None:
            return val  # Optional field — allow if missing

        pattern = r"^\d{2,3}/\d{2,3}$"
        if not re.match(pattern, val):
            raise ValueError("Invalid blood pressure format. Expected '120/80'")

        systolic, diastolic = map(int, val.split("/"))
        if systolic < 80 or systolic > 300 or diastolic < 40 or diastolic > 150:
            raise ValueError("Blood pressure values out of valid range")

        return val

    # Foreign key to Donor
    donor_id: int = Field(..., description="ID of the donor who made the donation")


class DonationCreate(DonationBase):
    pass


class DonationUpdate(DonationBase):
    updated_at: datetime.datetime


class DonationOut(DonationBase):
    id: int
    updated_at: datetime.datetime

    class Config:
        orm_mode = True
