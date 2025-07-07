# Blood Donation FastAPI Service

A modern, async-first RESTful API for blood donation management, built with **FastAPI**, **Async SQLAlchemy**, and **SQLite**.
Supports full CRUD for donors and their donations, with input validation, structured logging, OpenTelemetry tracing, and full test coverage.

---

## Features

- **Donor CRUD:** Create, list (paginated), update, and delete donors
- **Donation Management:** Record and update donations, with validations for hemoglobin, blood pressure, pulse, and more
- **Async SQLAlchemy:** Fully asynchronous database operations
- **Validation:** Strict data validation
- **Logging:** logs with per-request correlation IDs
- **OpenTelemetry:** Tracing support with console and OTLP exporters
- **Health Check:** `/health` endpoint for database connectivity
- **Tested:** Async API and service layer tests with pytest and httpx
- **Easy DB Setup:** Bootstrap & seed the database from CLI

---

## Getting Started

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd <repo-name>
poetry install

```

### 2. Configure Environment
Copy .env.example to .env and adjust as needed:

### 3. Initialize the Database
Creates all tables and seeds example data.
```bash
python app/db/bootstrap_db.py
```

### 4. Run the Application
```bash
uvicorn app.main:app --reload
```
Visit http://127.0.0.1:8000/docs for the interactive API docs.

## API Overview
### Donor Endpoints
- POST /api/v1/donors — Create new donor
- GET /api/v1/donors — List donors (paginated, use skip and limit)
- GET /api/v1/donors/{donor_id} — Get donor by ID
- PUT /api/v1/donors/{donor_id} — Update donor
- DELETE /api/v1/donors/{donor_id} — Delete donor (only if no donations)

### Donation Endpoints
- POST /api/v1/donors/{donor_id}/donations — Add a donation for a donor
- PUT /api/v1/donations/{donation_id} — Update a donation
- DELETE /api/v1/donations/{donation_id} — Delete a donation

### Health Check
- GET /health — Returns {"status": "ok"} if DB is up

## Testing
### Install test dependencies:

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock httpx
```

### Run tests:
```bash
pytest
```