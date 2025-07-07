import pytest
from fastapi import HTTPException
from pytest_mock import MockerFixture

from app.api.v1.schemas.donor_schema import DonationCreate, DonorCreate
from app.db.models.donor_models import Donation, Donor
from app.service.donor_service import (
    create_donation,
    create_donor,
    delete_donor,
    get_all_donors,
    get_donor,
)

# from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_create_donor_success(mocker: MockerFixture):
    db = mocker.AsyncMock()
    donor_data = DonorCreate(name="Alice", blood_group="A+", age=30, last_donated=None)
    donor_obj = Donor(id=1, name="Alice", blood_group="A+", age=30, last_donated=None)
    # donor_obj = Donor(**donor_data.model_dump())

    mocker.patch("app.service.donor_service.Donor", return_value=donor_obj)
    db.add = mocker.MagicMock()
    db.commit = mocker.AsyncMock()
    db.refresh = mocker.AsyncMock()
    # Test
    donor = await create_donor(db, donor_data)
    assert getattr(donor, "name", None) == "Alice"
    db.add.assert_called()
    db.commit.assert_called()
    db.refresh.assert_called_with(donor_obj)


@pytest.mark.asyncio
async def test_get_all_donors(mocker):
    db = mocker.AsyncMock()
    donors = [
        Donor(id=1, name="A", blood_group="A+", age=25),
        Donor(id=2, name="B", blood_group="O-", age=32),
    ]
    result = mocker.MagicMock()
    scalars_mock = mocker.MagicMock()
    scalars_mock.all.return_value = donors
    result.scalars.return_value = scalars_mock
    db.execute.return_value = result
    # Test
    fetched = await get_all_donors(db)
    assert fetched == donors
    db.execute.assert_called()


@pytest.mark.asyncio
async def test_get_donor_found(mocker: MockerFixture):
    db = mocker.AsyncMock()
    donor = Donor(id=1, name="A", blood_group="A+", age=25)
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = donor
    db.execute.return_value = result
    fetched = await get_donor(db, 1)
    assert fetched == donor


@pytest.mark.asyncio
async def test_get_donor_not_found(mocker):
    db = mocker.AsyncMock()
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    fetched = await get_donor(db, 1234)
    assert fetched is None


@pytest.mark.asyncio
async def test_delete_donor_no_donations(mocker):
    db = mocker.AsyncMock()
    donor = Donor(id=1, name="A", blood_group="A+", age=25)
    donor.donations = []
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = donor
    db.execute.return_value = result
    db.delete = mocker.AsyncMock()
    db.commit = mocker.AsyncMock()
    resp = await delete_donor(db, 1)
    assert resp == {"detail": "Donor deleted successfully"}
    db.delete.assert_called_with(donor)
    db.commit.assert_called()


@pytest.mark.asyncio
async def test_delete_donor_with_donations(mocker):
    db = mocker.AsyncMock()
    donor = Donor(id=1, name="A", blood_group="A+", age=25)
    donor.donations = [
        Donation(id=1, donor_id=1, date=None, volume_ml=500, location="X")
    ]
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = donor
    db.execute.return_value = result
    with pytest.raises(HTTPException) as exc:
        await delete_donor(db, 1)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_create_donation_success(mocker):
    db = mocker.AsyncMock()
    import datetime

    donation_in = DonationCreate(
        date=datetime.date(2024, 7, 1),
        volume_ml=500,
        location="Test",
        donor_id=100,
        hemoglobin=13.0,
        pulse=70,
        blood_pressure="120/80",
    )
    donation_obj = Donation(
        id=1,
        date=datetime.date(2024, 7, 1),
        volume_ml=500,
        location="Test",
        donor_id=100,
    )
    mocker.patch("app.service.donor_service.Donation", return_value=donation_obj)
    db.add = mocker.AsyncMock()
    db.commit = mocker.AsyncMock()
    db.refresh = mocker.AsyncMock()
    result = await create_donation(db, 100, donation_in)
    assert result == donation_obj
    db.add.assert_called()
    db.commit.assert_called()
    db.refresh.assert_called_with(donation_obj)
