# Polyglot Persistence CRUD Demo

A **Product / Inventory Management System** that demonstrates **polyglot persistence** — using 4 different databases, each for the workload it excels at.

---

## Architecture

```
Browser
  │
  ▼
React SPA (Vite · Nginx · port 3000)
  │
  │  HTTP / REST
  ▼
FastAPI  (Python · Uvicorn · port 8000)
  │
  ├──► PostgreSQL ──► products, categories, suppliers
  │     (ACID, FK, constraints)
  │
  ├──► MySQL ──────► orders, order_items
  │     (transactions, aggregation, reporting)
  │
  ├──► MongoDB ───► product_events
  │     (flexible schema, append-only audit log)
  │
  └──► Redis ─────► product:{id}, products:list
        (in-memory cache, TTL-based invalidation)
```

---

## Why 4 Databases?

| Database | Responsibility | Why |
|----------|---------------|-----|
| **PostgreSQL** | Core product catalog | ACID transactions, FK constraints, complex JOINs |
| **MySQL** | Orders & sales | Relational reporting, aggregation, e-commerce workloads |
| **MongoDB** | Product event history | Flexible/heterogeneous document schema, append-only |
| **Redis** | Read cache | Sub-millisecond reads, TTL, cache invalidation |

See [`docs/database-architecture.md`](docs/database-architecture.md) for the full explanation.

---

## Project Structure

```
basic_web/
├── backend/          # Python FastAPI service
│   ├── app/
│   │   ├── api/      # Route handlers (products, orders, events, health)
│   │   ├── database/ # DB clients (postgres, mysql, mongodb, redis)
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic request/response schemas
│   │   ├── services/ # Business logic (product, order, event, cache)
│   │   ├── config.py # Settings via pydantic-settings
│   │   └── main.py   # FastAPI app + lifespan
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/         # React 18 + Vite SPA
│   ├── src/
│   │   ├── components/  # Navbar, Toast, EventTimeline, …
│   │   ├── hooks/       # useProducts, useOrders
│   │   ├── pages/       # Dashboard, ProductList, ProductForm, ProductDetail, OrderList
│   │   └── services/    # api.js (Axios)
│   ├── Dockerfile       # Multi-stage: Node build → Nginx serve
│   └── nginx.conf
│
├── database/
│   ├── postgres/schema.sql
│   ├── mysql/schema.sql
│   └── mongodb/README.md
│
├── scripts/
│   └── seed_data.py   # Seed all 4 databases
│
├── docs/
│   └── database-architecture.md
│
├── docker-compose.yml  # frontend + backend only (no DB containers)
├── .env.example
└── .gitignore
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Docker | 24+ |
| Docker Compose | v2 |
| Python | 3.11+ (for seed script only) |

You must provision and have connection details for:
- PostgreSQL server
- MySQL server
- MongoDB server
- Redis server

---

## 1. Database Setup

### PostgreSQL

```bash
# Connect as admin
psql -h <host> -U postgres

# Create DB and user
CREATE DATABASE polyglot_db;
CREATE USER polyglot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE polyglot_db TO polyglot_user;

# Apply schema
psql -h <host> -U polyglot_user -d polyglot_db -f database/postgres/schema.sql
```

### MySQL

```bash
# Connect as root
mysql -h <host> -u root -p

# Create DB and user
CREATE DATABASE polyglot_orders CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'polyglot_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON polyglot_orders.* TO 'polyglot_user'@'%';
FLUSH PRIVILEGES;

# Apply schema
mysql -h <host> -u polyglot_user -p polyglot_orders < database/mysql/schema.sql
```

### MongoDB

Follow the instructions in [`database/mongodb/README.md`](database/mongodb/README.md).

### Redis

No schema needed. Just ensure the server is accessible and note the host/port/password.

---

## 2. Environment Configuration

```bash
# Root-level (for docker-compose)
cp .env.example .env
# Edit .env with your real DB credentials

# Backend (for local dev without Docker)
cp backend/.env.example backend/.env
# Edit backend/.env
```

---

## 3. Seed Sample Data

```bash
# Install dependencies (use a virtualenv)
pip install asyncpg aiomysql motor redis

# Run seed script (reads .env vars)
env $(cat backend/.env | xargs) python scripts/seed_data.py
```

This inserts:
- 4 categories, 3 suppliers, **20 products** → PostgreSQL
- **30 orders** with items → MySQL
- **~100 product events** → MongoDB
- Cache for first 5 products → Redis

---

## 4. Build Docker Images

```bash
# Build backend
docker build -t polyglot-backend ./backend

# Build frontend
docker build -t polyglot-frontend ./frontend
```

---

## 5. Run with Docker Compose

```bash
# Start backend + frontend (databases are external)
docker compose up -d

# Check logs
docker compose logs -f

# Verify all DBs are connected
curl http://localhost:8000/ready
```

---

## 6. Run Services Manually (without Compose)

```bash
# Backend
docker run \
  --env-file backend/.env \
  -p 8000:8000 \
  --name polyglot-backend \
  polyglot-backend

# Frontend
docker run \
  -p 3000:80 \
  --name polyglot-frontend \
  polyglot-frontend
```

Open browser: **http://localhost:3000**

---

## 7. API Documentation

FastAPI auto-generates interactive docs:

| URL | Description |
|-----|-------------|
| `http://localhost:8000/api/docs` | Swagger UI |
| `http://localhost:8000/api/redoc` | ReDoc |

### Key Endpoints

| Method | Path | Database | Description |
|--------|------|----------|-------------|
| `GET` | `/api/products` | Redis → PostgreSQL | List products (cached) |
| `GET` | `/api/products/{id}` | Redis → PostgreSQL | Product detail (cached) |
| `POST` | `/api/products` | PostgreSQL + MongoDB + Redis | Create product |
| `PUT` | `/api/products/{id}` | PostgreSQL + MongoDB + Redis | Update product |
| `DELETE` | `/api/products/{id}` | PostgreSQL + MongoDB + Redis | Delete product |
| `GET` | `/api/products/{id}/events` | MongoDB | Product event history |
| `GET` | `/api/products/{id}/sales` | MySQL | Sales summary |
| `GET` | `/api/orders` | MySQL | List orders |
| `POST` | `/api/orders` | MySQL | Create order |
| `GET` | `/health` | — | Liveness probe |
| `GET` | `/ready` | All 4 DBs | Readiness probe |

---

## 8. Data Flow

### Create Product

```
POST /api/products
  │
  ├─► INSERT INTO products (PostgreSQL)  ← primary store
  ├─► insert product_events doc (MongoDB) ← audit log
  └─► DEL products:list (Redis)          ← cache invalidation
```

### Get Product Detail

```
GET /api/products/:id
  │
  ├─► GET product:{id} from Redis ── HIT ──► return JSON (< 1ms)
  │
  └─► MISS
        │
        └─► SELECT from PostgreSQL
              │
              └─► SET product:{id} in Redis (TTL=300s)
                    │
                    └─► return JSON
```

### Update Product

```
PUT /api/products/:id
  │
  ├─► UPDATE products (PostgreSQL)
  ├─► insert product_updated event (MongoDB)
  ├─► insert price_changed event IF price changed (MongoDB)
  ├─► insert stock_updated event IF stock changed (MongoDB)
  ├─► DEL product:{id} (Redis)
  └─► DEL products:list (Redis)
```

---

## 9. Deployment on External Cloud DBs (e.g. CMC Cloud)

1. **Provision** PostgreSQL, MySQL, MongoDB, Redis as managed services
2. **Note** each service's hostname, port, username, password, database name
3. **Configure** your `.env` or inject environment variables directly:

```bash
docker run \
  -e POSTGRES_HOST=pg.cmc.cloud \
  -e POSTGRES_DB=polyglot_db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secret \
  -e MYSQL_HOST=mysql.cmc.cloud \
  ...
  -p 8000:8000 \
  polyglot-backend
```

4. **Network**: Ensure backend container can reach all 4 DB hosts (security groups / firewall rules)
5. **Verify**: `curl http://localhost:8000/ready` should show all 4 databases as `healthy`

---

## 10. Resilience Design

| Failure | Behavior |
|---------|----------|
| Redis down | Application continues; all reads hit PostgreSQL |
| MongoDB down | CRUD succeeds; event logging silently skipped |
| PostgreSQL down | Product APIs return 503 |
| MySQL down | Order APIs return 503; product APIs unaffected |

---

## License

MIT
