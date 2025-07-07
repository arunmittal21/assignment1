import datetime

import pytest
from fastapi import HTTPException
from pytest_mock import MockerFixture

from app.api.v1.schemas.donor_schema import (
    DonationCreate,
    DonationUpdate,
    DonorCreate,
    DonorUpdate,
)
from app.db.models.donor_models import Donation, Donor
from app.service.donor_service import (
    create_donation,
    create_donor,
    delete_donation,
    delete_donor,
    get_all_donors,
    get_donation,
    get_donor,
    get_total_donor_count,
    update_donation,
    update_donor,
)

# ========== DONOR TESTS ==========


@pytest.mark.asyncio
async def test_create_donor_success(mocker: MockerFixture):
    db = mocker.AsyncMock()
    donor_data = DonorCreate(
        name="Alice",
        blood_group="A+",
        age=30,
        last_donated=None,
    )
    donor_obj = Donor(id=1, name="Alice", blood_group="A+", age=30, last_donated=None)
    mocker.patch("app.service.donor_service.Donor", return_value=donor_obj)
    db.add = mocker.MagicMock()
    db.commit = mocker.AsyncMock()
    db.refresh = mocker.AsyncMock()
    donor = await create_donor(db, donor_data)
    assert donor.name == "Alice"  # type: ignore
    db.add.assert_called()
    db.commit.assert_called()
    db.refresh.assert_called_with(donor_obj)


@pytest.mark.asyncio
async def test_create_donor_exception(mocker):
    db = mocker.AsyncMock()
    donor_data = DonorCreate(
        name="Fail",
        blood_group="A+",
        age=30,
        last_donated=None,
    )
    mocker.patch("app.service.donor_service.Donor", side_effect=Exception("DB fail"))
    with pytest.raises(Exception):
        await create_donor(db, donor_data)


@pytest.mark.asyncio
async def test_get_all_donors(mocker):
    db = mocker.AsyncMock()
    donors = [
        Donor(id=-1, name="A", blood_group="A+", age=25),
        Donor(id=-2, name="B", blood_group="O-", age=32),
    ]
    result = mocker.MagicMock()
    scalars_mock = mocker.MagicMock()
    scalars_mock.all.return_value = donors
    result.scalars.return_value = scalars_mock
    db.execute.return_value = result
    fetched = await get_all_donors(db)
    assert fetched == donors
    db.execute.assert_called()


@pytest.mark.asyncio
async def test_get_all_donors_exception(mocker):
    db = mocker.AsyncMock()
    db.execute.side_effect = Exception("Query error")
    with pytest.raises(Exception):
        await get_all_donors(db)


@pytest.mark.asyncio
async def test_get_donor_found(mocker: MockerFixture):
    db = mocker.AsyncMock()
    donor = Donor(id=1, name="A", blood_group="A+", age=25)
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = donor
    db.execute.return_value = result
    fetched = await get_donor(db, 1)
    assert fetched == donor
    db.execute.assert_called()


@pytest.mark.asyncio
async def test_get_donor_not_found_raises(mocker):
    db = mocker.AsyncMock()
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    with pytest.raises(HTTPException) as exc:
        await get_donor(db, 999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_donor_not_found_silent(mocker):
    db = mocker.AsyncMock()
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    fetched = await get_donor(db, 999, raise_error_when_not_found=False)
    assert fetched is None


@pytest.mark.asyncio
async def test_get_donor_exception(mocker):
    db = mocker.AsyncMock()
    db.execute.side_effect = Exception("Failed query")
    with pytest.raises(Exception):
        await get_donor(db, 1)


@pytest.mark.asyncio
async def test_update_donor_success(mocker):
    db = mocker.AsyncMock()
    donor_obj = Donor(id=1, name="A", blood_group="A+", age=25)
    donor_data = DonorUpdate(
        name="Bob",
        blood_group="O+",
        age=40,
        last_donated=None,
        updated_at=datetime.datetime.utcnow(),
    )
    mocker.patch("app.service.donor_service.get_donor", return_value=donor_obj)
    db.commit = mocker.AsyncMock()
    db.refresh = mocker.AsyncMock()
    donor = await update_donor(db, 1, donor_data)
    assert donor.name == "Bob"  # type: ignore
    db.commit.assert_called()
    db.refresh.assert_called_with(donor_obj)


@pytest.mark.asyncio
async def test_update_donor_exception(mocker):
    db = mocker.AsyncMock()
    mocker.patch("app.service.donor_service.get_donor", side_effect=Exception("fail"))
    donor_data = DonorUpdate(
        name="Bob",
        blood_group="O+",
        age=40,
        last_donated=None,
        updated_at=datetime.datetime.utcnow(),
    )
    with pytest.raises(Exception):
        await update_donor(db, 1, donor_data)


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
        Donation(
            id=1,
            donor_id=1,
            date=datetime.date.today(),
            volume_ml=500,
            location="Test",
            updated_at=datetime.datetime.utcnow(),
        )
    ]
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = donor
    db.execute.return_value = result
    with pytest.raises(HTTPException) as exc:
        await delete_donor(db, 1)
    assert exc.value.status_code == 400
    assert "Cannot delete donor with existing donations" in exc.value.detail


@pytest.mark.asyncio
async def test_delete_donor_exception(mocker):
    db = mocker.AsyncMock()
    mocker.patch("app.service.donor_service.get_donor", side_effect=Exception("fail"))
    with pytest.raises(Exception):
        await delete_donor(db, 1)


@pytest.mark.asyncio
async def test_get_total_donor_count(mocker):
    db = mocker.AsyncMock()
    result = mocker.MagicMock()
    result.scalar_one.return_value = 123
    db.execute.return_value = result
    total = await get_total_donor_count(db)
    assert total == 123


# ========== DONATION TESTS ==========


@pytest.mark.asyncio
async def test_create_donation_success(mocker):
    db = mocker.AsyncMock()
    donation_in = DonationCreate(
        date=datetime.date.today(),
        volume_ml=500,
        location="Test",
        donor_id=100,
        hemoglobin=13.0,
        pulse=70,
        blood_pressure="120/80",
    )
    donation_obj = Donation(
        id=1,
        donor_id=100,
        date=donation_in.date,
        volume_ml=donation_in.volume_ml,
        location=donation_in.location,
        updated_at=datetime.datetime.utcnow(),
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


@pytest.mark.asyncio
async def test_create_donation_exception(mocker):
    db = mocker.AsyncMock()
    donation_in = DonationCreate(
        date=datetime.date.today(),
        volume_ml=500,
        location="Test",
        donor_id=100,
        hemoglobin=13.0,
        pulse=70,
        blood_pressure="120/80",
    )
    mocker.patch("app.service.donor_service.Donation", side_effect=Exception("fail"))
    with pytest.raises(Exception):
        await create_donation(db, 100, donation_in)


@pytest.mark.asyncio
async def test_get_donation_found(mocker):
    db = mocker.AsyncMock()
    donation = Donation(
        id=1,
        donor_id=1,
        date=datetime.date.today(),
        volume_ml=500,
        location="X",
        updated_at=datetime.datetime.utcnow(),
    )
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = donation
    db.execute.return_value = result
    got = await get_donation(db, 1)
    assert got == donation


@pytest.mark.asyncio
async def test_get_donation_not_found_raises(mocker):
    db = mocker.AsyncMock()
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    with pytest.raises(HTTPException):
        await get_donation(db, 555)


@pytest.mark.asyncio
async def test_get_donation_not_found_silent(mocker):
    db = mocker.AsyncMock()
    result = mocker.MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    got = await get_donation(db, 555, raise_error_when_not_found=False)
    assert got is None


@pytest.mark.asyncio
async def test_update_donation_success(mocker):
    db = mocker.AsyncMock()
    donation_obj = Donation(
        id=1,
        donor_id=1,
        date=datetime.date.today(),
        volume_ml=500,
        location="A",
        updated_at=datetime.datetime.utcnow(),
    )
    donation_in = DonationUpdate(
        date=datetime.date.today(),
        volume_ml=400,
        location="Bombay",
        donor_id=1,
        hemoglobin=14.5,
        pulse=72,
        blood_pressure="110/80",
        updated_at=datetime.datetime.utcnow(),
    )
    mocker.patch("app.service.donor_service.get_donation", return_value=donation_obj)
    db.commit = mocker.AsyncMock()
    db.refresh = mocker.AsyncMock()
    updated = await update_donation(db, 1, donation_in)
    assert updated.location == "Bombay"  # type: ignore
    db.commit.assert_called()
    db.refresh.assert_called_with(donation_obj)


@pytest.mark.asyncio
async def test_update_donation_exception(mocker):
    db = mocker.AsyncMock()
    mocker.patch(
        "app.service.donor_service.get_donation", side_effect=Exception("fail")
    )
    donation_in = DonationUpdate(
        date=datetime.date.today(),
        volume_ml=400,
        location="Bombay",
        donor_id=1,
        hemoglobin=14.5,
        pulse=72,
        blood_pressure="110/80",
        updated_at=datetime.datetime.utcnow(),
    )
    with pytest.raises(Exception):
        await update_donation(db, 1, donation_in)


@pytest.mark.asyncio
async def test_delete_donation_success(mocker):
    db = mocker.AsyncMock()
    donation = Donation(
        id=2,
        donor_id=2,
        date=datetime.date.today(),
        volume_ml=450,
        location="Test",
        updated_at=datetime.datetime.utcnow(),
    )
    mocker.patch("app.service.donor_service.get_donation", return_value=donation)
    db.delete = mocker.AsyncMock()
    db.commit = mocker.AsyncMock()
    resp = await delete_donation(db, 2)
    assert resp == {"detail": "Donation deleted successfully"}
    db.delete.assert_called_with(donation)
    db.commit.assert_called()


@pytest.mark.asyncio
async def test_delete_donation_exception(mocker):
    db = mocker.AsyncMock()
    mocker.patch(
        "app.service.donor_service.get_donation", side_effect=Exception("fail")
    )
    with pytest.raises(Exception):
        await delete_donation(db, 2)
