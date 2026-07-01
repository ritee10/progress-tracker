# Skill Progress Tracker - Backend

This is the production-grade FastAPI backend for the **Skill Progress Tracker** platform.

## Features Included
- **FastAPI** with async architecture
- **PostgreSQL** configured with `asyncpg`
- **SQLAlchemy 2.0** ORM
- **Alembic** for migrations
- **Pydantic v2** schemas
- **JWT Authentication** and Role-Based Access Control
- Modular monolith design (Routers → Services → Repositories)

## Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (if not using Docker)

## Setup Instructions

### 1. Environment Configuration
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Ensure `DATABASE_URL` is set correctly.

### 2. Local Setup (Without Docker)

Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Database Migrations (Alembic)
To initialize alembic (if not already initialized):
```bash
alembic init -t async alembic
```
*(Make sure to configure `alembic.ini` and `alembic/env.py` with the async database URL from config)*

Run migrations:
```bash
alembic upgrade head
```

### 4. Running the Application
```bash
uvicorn app.main:app --reload
```
The API will be available at: http://localhost:8000
Swagger Docs: http://localhost:8000/docs

### 5. Running via Docker Compose
To run the entire stack (Backend, Postgres, Redis):
```bash
docker-compose up --build
```

### 6. Running Tests
```bash
pytest
```
*(You may need to create a `conftest.py` with mock clients and test DB setup)*
