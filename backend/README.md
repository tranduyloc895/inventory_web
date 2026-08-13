# Polyglot Persistence CRUD API

This is the backend for a Product/Inventory Management System using Polyglot Persistence.

## Tech Stack
- Python 3.11 + FastAPI
- PostgreSQL (Asyncpg) - Core Master Data (Products, Categories)
- MySQL (Aiomysql) - Transactional Data (Orders)
- MongoDB (Motor) - Event Store / Audit Log
- Redis (redis.asyncio) - Caching Layer

## Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environments:
   Copy `.env.example` to `.env` and fill in DB credentials.
3. Run locally:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Docker Setup
```bash
docker build -t polyglot-api .
docker run -p 8000:8000 --env-file .env polyglot-api
```
