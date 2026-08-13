# Database Architecture – Polyglot Persistence Design

## Overview

This application deliberately uses **four different databases**, each chosen for a specific workload that plays to its strengths. This design pattern is called **Polyglot Persistence** — using the right tool for the right job rather than forcing a single database to handle all workloads.

---

## The One-Database Trap

Before explaining our design, consider what would happen if we used only PostgreSQL for everything:

| Workload | Problem with single DB |
|----------|------------------------|
| Product audit history (flexible metadata) | Schema migrations every time event structure changes |
| Cache / fast reads | Expensive SELECT on every page load |
| Event log (append-only, huge volume) | Bloats primary DB; affects OLTP performance |
| Sales reporting | Acceptable, but MySQL has better tooling in some ecosystems |

A single database works — but it means trade-offs: either rigid schema for flexible data, or cache implemented in application memory (lost on restart), or mixing OLTP and analytics traffic.

---

## Database Responsibility Map

```
                    ┌─────────────────────────────────────────────────┐
                    │              Backend (FastAPI)                   │
                    └──────┬────────────┬────────────┬────────────────┘
                           │            │            │            │
                           ▼            ▼            ▼            ▼
                      PostgreSQL     MySQL       MongoDB        Redis
                      (Primary)   (Reporting)   (Events)      (Cache)
```

---

## PostgreSQL — Core Product Catalog

**Responsibility**: Primary relational database for structured business data.

**Tables**: `products`, `categories`, `suppliers`

**Why PostgreSQL?**
- **ACID transactions**: Price updates and stock adjustments must be atomic
- **Foreign key constraints**: `products.category_id → categories.id` prevents orphaned data
- **CHECK constraints**: `price >= 0`, `stock >= 0` enforced at DB level
- **Complex JOINs**: Product list queries join categories and suppliers
- **Mature ecosystem**: Excellent tooling, backup strategies, and cloud support (RDS, Cloud SQL, Supabase)
- **JSON support**: Future flexibility if product attributes need semi-structured storage

**Data flow**:
```
POST /api/products
  → INSERT INTO products (PostgreSQL)
  → Cache invalidation (Redis)
  → Event log (MongoDB)
```

**When NOT to use**:
- Storing millions of flexible-schema log entries (→ MongoDB)
- Sub-millisecond key-value lookups (→ Redis)

---

## MySQL — Orders & Sales Reporting

**Responsibility**: Transactional order data with aggregation/reporting queries.

**Tables**: `orders`, `order_items`

**Why MySQL for orders (and not PostgreSQL)?**

In real-world polyglot architectures, different teams or systems own different databases. Here we demonstrate that:

1. **MySQL excels at write-heavy transactional workloads** common in e-commerce: millions of orders, tight SLA for checkout
2. **Reporting queries** (`GROUP BY product_id, SUM(quantity)`) perform well with MySQL's InnoDB engine
3. **Denormalized order snapshot**: `order_items.product_name` is stored at order time — MySQL's row-level locking makes this pattern safe
4. **Cross-database reference**: `order_items.product_id` references PostgreSQL's `products.id` without a foreign key — application enforces consistency, demonstrating the trade-off in distributed data

**Example reporting query**:
```sql
SELECT product_id, SUM(quantity) AS sold, SUM(subtotal) AS revenue
FROM order_items
JOIN orders ON orders.id = order_items.order_id
WHERE orders.status = 'completed'
GROUP BY product_id;
```

**When NOT to use**:
- Flexible/schema-less event data (→ MongoDB)
- Caching (→ Redis)

---

## MongoDB — Product Event / Audit Log

**Responsibility**: Append-only audit trail with flexible, heterogeneous document structure.

**Collection**: `product_events`

**Why MongoDB?**
- **Schema flexibility**: `price_changed` events have `{old_price, new_price}`; `stock_updated` has `{old_stock, new_stock, reason}` — different fields per event type. In SQL this requires either a wide nullable table or an EAV pattern (both ugly).
- **Append-only pattern**: Events are never updated. MongoDB is optimized for insert-heavy workloads.
- **Native JSON**: Events map directly to JSON documents — no ORM mapping needed.
- **TTL index**: Old events can automatically expire via MongoDB's built-in TTL index.
- **Horizontal scaling**: Event logs grow indefinitely. MongoDB's sharding handles petabyte-scale audit logs.

**Events logged**:
| Event | Trigger | Metadata |
|-------|---------|----------|
| `product_created` | POST /api/products | name, price, stock, sku |
| `product_updated` | PUT /api/products/:id | changed fields |
| `price_changed` | PUT (price changed) | old_price, new_price |
| `stock_updated` | PUT (stock changed) | old_stock, new_stock, delta |
| `product_deleted` | DELETE /api/products/:id | name, sku |

**Resilience**: MongoDB event logging is **non-critical**. If MongoDB is unavailable, the CRUD operation still succeeds. The event is simply not recorded. This is an intentional trade-off: audit completeness vs. application availability.

---

## Redis — Cache Layer

**Responsibility**: In-memory cache for frequently read product data.

**Keys**:
- `product:{id}` — single product detail (TTL: 300s default)
- `products:list` — full product list (TTL: 300s default)

**Why Redis?**
- **Sub-millisecond reads**: Redis returns cached data in <1ms vs. 5-20ms for PostgreSQL
- **TTL-based expiration**: Cache entries automatically expire, preventing stale data accumulation
- **Cache invalidation**: On write (create/update/delete), specific keys are deleted
- **Simple data model**: Product JSON fits perfectly as a Redis string value
- **Reduces DB load**: Protects PostgreSQL from thundering-herd on popular products

**Cache flow**:
```
GET /api/products/:id
  │
  ├─ Redis HIT  → return JSON (< 1ms)
  │
  └─ Redis MISS
        │
        └─ SELECT from PostgreSQL
              │
              └─ SET in Redis (TTL=300s)
                    │
                    └─ return JSON
```

**Cache invalidation**:
```
PUT /api/products/:id   → DEL product:{id}, DEL products:list
POST /api/products      → DEL products:list
DELETE /api/products/:id → DEL product:{id}, DEL products:list
```

**Resilience**: Redis is a **performance optimization layer**, not source of truth. If Redis is unavailable:
- All reads fall back to PostgreSQL
- All writes proceed normally (just without cache)
- Application logs a warning but continues running

---

## Summary Table

| Database | Role | Workload Type | Key Strength |
|----------|------|--------------|--------------|
| **PostgreSQL** | Primary product catalog | OLTP + complex queries | ACID, FK, constraints |
| **MySQL** | Orders & sales | OLTP + reporting | Aggregation, e-commerce ecosystem |
| **MongoDB** | Event/audit history | Append-only, schema-less | Flexible documents, horizontal scale |
| **Redis** | Cache | In-memory key-value | Sub-ms reads, TTL, atomic ops |

---

## Architecture Diagram

```
Browser
  │
  ▼
React SPA (Vite, Nginx)
  │
  │ HTTP / REST
  ▼
FastAPI (Python)
  │
  ├──► PostgreSQL ──► products, categories, suppliers
  │     (primary)     ACID, FK, transactions
  │
  ├──► MySQL ─────► orders, order_items
  │    (orders)     aggregation, reporting
  │
  ├──► MongoDB ───► product_events
  │    (events)     flexible schema, append-only
  │
  └──► Redis ─────► product:{id}, products:list
       (cache)      TTL, invalidation, fast reads
```
