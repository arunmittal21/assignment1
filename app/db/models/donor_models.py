from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    blood_group = Column(String(3), nullable=False)
    age = Column(Integer, nullable=False)
    last_donated = Column(Date, nullable=True)

    donations = relationship(
        "Donation", back_populates="donor", cascade="all, delete-orphan"
    )


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(
        Integer, ForeignKey("donors.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False)
    volume_ml = Column(Integer, nullable=False)
    location = Column(String(100), nullable=False)
    hemoglobin = Column(Integer, nullable=True)
    pulse = Column(Integer, nullable=True)
    blood_pressure = Column(String(10), nullable=True)  # Format: 'systolic/diastolic'

    donor = relationship("Donor", back_populates="donations")
