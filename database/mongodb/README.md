# MongoDB Setup – Polyglot Persistence Demo

MongoDB is used as the **event store / audit log** for product activity.

## Why MongoDB for this workload?

| Reason | Detail |
|--------|--------|
| **Flexible schema** | Each event type has different `metadata` fields — no rigid columns needed |
| **Append-only writes** | Product events are never updated, only inserted — perfect for document stores |
| **Native JSON** | Events are naturally JSON-shaped with nested metadata |
| **Horizontal scalability** | Event logs grow indefinitely; MongoDB shards well |
| **Time-series queries** | TTL indexes and range queries on `timestamp` are efficient |

## Collection: `product_events`

No fixed schema — documents look like this depending on the event type:

```json
// product_created
{
  "_id": ObjectId("..."),
  "product_id": 42,
  "event_type": "product_created",
  "timestamp": ISODate("2025-01-15T10:00:00Z"),
  "metadata": {
    "name": "Wireless Mouse",
    "price": 25.99,
    "stock": 100,
    "sku": "WM-001"
  }
}

// price_changed
{
  "_id": ObjectId("..."),
  "product_id": 42,
  "event_type": "price_changed",
  "timestamp": ISODate("2025-01-20T14:30:00Z"),
  "metadata": {
    "old_price": 25.99,
    "new_price": 29.99
  }
}

// stock_updated
{
  "_id": ObjectId("..."),
  "product_id": 42,
  "event_type": "stock_updated",
  "timestamp": ISODate("2025-01-22T09:15:00Z"),
  "metadata": {
    "old_stock": 100,
    "new_stock": 85,
    "delta": -15
  }
}

// product_deleted
{
  "_id": ObjectId("..."),
  "product_id": 42,
  "event_type": "product_deleted",
  "timestamp": ISODate("2025-02-01T11:00:00Z"),
  "metadata": {
    "name": "Wireless Mouse",
    "sku": "WM-001"
  }
}
```

## Setup Instructions

### 1. Connect to MongoDB

```bash
mongosh "mongodb://<host>:<port>" --username <user> --authenticationDatabase admin
```

### 2. Create database and user

```javascript
use admin

db.createUser({
  user: "polyglot_user",
  pwd: "your_password",
  roles: [
    { role: "readWrite", db: "polyglot_events" }
  ]
})

// Switch to application DB
use polyglot_events
```

### 3. Create indexes (recommended)

```javascript
use polyglot_events

// Index for querying events by product
db.product_events.createIndex({ "product_id": 1, "timestamp": -1 })

// Index for time-range queries
db.product_events.createIndex({ "timestamp": -1 })

// Index for filtering by event type
db.product_events.createIndex({ "event_type": 1 })

// Optional: TTL index to auto-expire old events after 1 year (365 days)
// db.product_events.createIndex(
//   { "timestamp": 1 },
//   { expireAfterSeconds: 31536000 }
// )
```

### 4. Verify setup

```javascript
db.product_events.stats()
db.product_events.getIndexes()
```

### 5. Configure environment variables

```env
MONGO_HOST=<your-mongodb-host>
MONGO_PORT=27017
MONGO_DB=polyglot_events
MONGO_USER=polyglot_user
MONGO_PASSWORD=your_password
MONGO_AUTH_SOURCE=admin
```

## Notes

- MongoDB is **non-critical** in this application: if MongoDB is unavailable, product CRUD operations continue normally. Event logging is **best-effort**.
- Events are **immutable** — they are only inserted, never updated or deleted.
- The backend uses **Motor** (async MongoDB driver) for non-blocking I/O.
