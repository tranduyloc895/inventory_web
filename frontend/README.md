# Polyglot Persistence Frontend

React + Vite frontend for the Polyglot Persistence CRUD application.

## Features
- Dashboard with multi-database health check
- Product Management (CRUD)
- Order Management
- View Event History (MongoDB)
- View Sales Summaries (MySQL)

## Setup
```bash
npm install
npm run dev
```

Ensure `.env` contains `VITE_API_BASE_URL=http://localhost:8000` (or your backend URL).

## Docker
Build and run via Docker or Docker Compose. The `nginx.conf` proxies `/api/` to `http://backend:8000/api/` by default.
