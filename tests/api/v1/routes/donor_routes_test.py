import pytest


# Sample donor and donation data for reuse
def sample_donor(
    name="Test Donor", blood_group="A+", age=25, last_donated="2024-05-01"
):
    return {
        "name": name,
        "blood_group": blood_group,
        "age": age,
        "last_donated": last_donated,
    }


def sample_donation(
    donor_id,
    date="2024-07-01",
    volume_ml=500,
    location="Test Location",
    hemoglobin=13.5,
    pulse=80,
    blood_pressure="120/80",
):
    return {
        "date": date,
        "volume_ml": volume_ml,
        "location": location,
        "hemoglobin": hemoglobin,
        "pulse": pulse,
        "blood_pressure": blood_pressure,
        "donor_id": donor_id,
    }


@pytest.mark.anyio
async def test_create_and_list_donors(client):
    donor_resp = await client.post("/api/v1/donors", json=sample_donor())
    assert donor_resp.status_code == 200
    donor = donor_resp.json()
    assert donor["name"] == "Test Donor"
    assert donor["blood_group"] == "A+"

    # List donors
    resp = await client.get("/api/v1/donors")
    assert resp.status_code == 200
    donors = resp.json()
    # assert len(donors) == 1
    assert any(d["id"] == donor["id"] and d["name"] == "Test Donor" for d in donors)


@pytest.mark.anyio
async def test_get_donor_by_id(client):
    donor_resp = await client.post("/api/v1/donors", json=sample_donor())
    donor_id = donor_resp.json()["id"]
    resp = await client.get(f"/api/v1/donors/{donor_id}")
    assert resp.status_code == 200
    donor = resp.json()
    assert donor["id"] == donor_id
    assert donor["name"] == "Test Donor"


@pytest.mark.anyio
async def test_get_donor_not_found(client):
    resp = await client.get("/api/v1/donors/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Donor not found"


@pytest.mark.anyio
async def test_create_donor_invalid_blood_group(client):
    data = sample_donor(blood_group="X-")
    resp = await client.post("/api/v1/donors", json=data)
    print(resp)
    assert resp.status_code == 422
    assert "Invalid blood group" in str(resp.json())


@pytest.mark.anyio
async def test_create_donation_for_donor(client):
    donor_resp = await client.post("/api/v1/donors", json=sample_donor())
    donor_id = donor_resp.json()["id"]
    donation_data = sample_donation(donor_id)
    resp = await client.post(f"/api/v1/donors/{donor_id}/donations", json=donation_data)
    assert resp.status_code == 200
    donation = resp.json()
    assert donation["donor_id"] == donor_id
    assert donation["volume_ml"] == 500
    assert donation["blood_pressure"] == "120/80"


@pytest.mark.anyio
async def test_create_donation_invalid_blood_pressure(client):
    donor_resp = await client.post("/api/v1/donors", json=sample_donor())
    donor_id = donor_resp.json()["id"]
    donation_data = sample_donation(donor_id, blood_pressure="abc")
    resp = await client.post(f"/api/v1/donors/{donor_id}/donations", json=donation_data)
    assert resp.status_code == 422
    assert "Invalid blood pressure format" in str(resp.json())


@pytest.mark.anyio
async def test_create_donation_invalid_hemoglobin(client):
    donor_resp = await client.post("/api/v1/donors", json=sample_donor())
    donor_id = donor_resp.json()["id"]
    donation_data = sample_donation(donor_id, hemoglobin=10.0)
    resp = await client.post(f"/api/v1/donors/{donor_id}/donations", json=donation_data)
    assert resp.status_code == 422
    assert "Hemoglobin must be between 12.0 and 20.0" in str(resp.json())


@pytest.mark.anyio
async def test_create_donation_invalid_pulse(client):
    donor_resp = await client.post("/api/v1/donors", json=sample_donor())
    donor_id = donor_resp.json()["id"]
    donation_data = sample_donation(donor_id, pulse=40)
    resp = await client.post(f"/api/v1/donors/{donor_id}/donations", json=donation_data)
    assert resp.status_code == 422
    assert "Pulse must be between 60 and 200" in str(resp.json())


@pytest.mark.skip(reason="Update and delete not implemented in routes")
async def test_update_donor(client):
    # To be implemented when update endpoint is available
    pass


@pytest.mark.skip(reason="Update and delete not implemented in routes")
async def test_delete_donor(client):
    # To be implemented when delete endpoint is available
    pass
