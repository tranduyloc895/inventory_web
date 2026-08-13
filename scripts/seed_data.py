#!/usr/bin/env python3
"""
seed_data.py – Polyglot Persistence Demo
=========================================
Populates all four databases with realistic sample data:
  • PostgreSQL : 4 categories, 3 suppliers, 20 products
  • MySQL      : 30 orders with order items
  • MongoDB    : ~100 product events
  • Redis      : warm product detail cache for first 5 products

Usage:
    # Reads env vars (same as backend)
    python scripts/seed_data.py

    # Or with an env file:
    env $(cat backend/.env | xargs) python scripts/seed_data.py
"""

import asyncio
import json
import logging
import os
import random
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Third-party imports (install same requirements as backend)
# ---------------------------------------------------------------------------
import asyncpg                          # PostgreSQL
import aiomysql                         # MySQL
from motor.motor_asyncio import AsyncIOMotorClient  # MongoDB
import redis.asyncio as aioredis        # Redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("seed")

# ---------------------------------------------------------------------------
# Config – read from environment variables (no hard-coding)
# ---------------------------------------------------------------------------

def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


PG_CONFIG = {
    "host":     env("POSTGRES_HOST", "localhost"),
    "port":     int(env("POSTGRES_PORT", "5432")),
    "database": env("POSTGRES_DB", "polyglot_db"),
    "user":     env("POSTGRES_USER", "postgres"),
    "password": env("POSTGRES_PASSWORD", "postgres"),
}

MY_CONFIG = {
    "host":   env("MYSQL_HOST", "localhost"),
    "port":   int(env("MYSQL_PORT", "3306")),
    "db":     env("MYSQL_DB", "polyglot_orders"),
    "user":   env("MYSQL_USER", "root"),
    "password": env("MYSQL_PASSWORD", "root"),
    "charset": "utf8mb4",
    "autocommit": False,
}

MONGO_HOST = env("MONGO_HOST", "localhost")
MONGO_PORT = int(env("MONGO_PORT", "27017"))
MONGO_DB   = env("MONGO_DB", "polyglot_events")
MONGO_USER = env("MONGO_USER", "")
MONGO_PASS = env("MONGO_PASSWORD", "")
MONGO_AUTH = env("MONGO_AUTH_SOURCE", "admin")

REDIS_HOST = env("REDIS_HOST", "localhost")
REDIS_PORT = int(env("REDIS_PORT", "6379"))
REDIS_PASS = env("REDIS_PASSWORD", "") or None
REDIS_DB   = int(env("REDIS_DB", "0"))
CACHE_TTL  = int(env("CACHE_TTL", "300"))

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {"name": "Electronics",     "description": "Electronic devices and accessories"},
    {"name": "Clothing",        "description": "Apparel and fashion items"},
    {"name": "Food & Beverage", "description": "Food products and drinks"},
    {"name": "Office Supplies", "description": "Stationery and office equipment"},
]

SUPPLIERS = [
    {"name": "TechPro Supplies",  "contact_email": "sales@techpro.example",    "phone": "+84-28-1234-5678"},
    {"name": "Global Fashion Co", "contact_email": "orders@globalfashion.example", "phone": "+84-24-9876-5432"},
    {"name": "FreshGoods VN",     "contact_email": "wholesale@freshgoods.example", "phone": "+84-90-1111-2222"},
]

PRODUCT_TEMPLATES = [
    # Electronics
    {"name": "Wireless Mouse",          "sku": "ELEC-WM-001", "description": "Ergonomic wireless mouse with 2.4GHz receiver", "price": 25.99,  "stock": 150, "cat": "Electronics", "sup": "TechPro Supplies"},
    {"name": "Mechanical Keyboard",     "sku": "ELEC-KB-002", "description": "Tenkeyless mechanical keyboard, Cherry MX Blue switches", "price": 89.99, "stock": 75,  "cat": "Electronics", "sup": "TechPro Supplies"},
    {"name": "USB-C Hub 7-in-1",        "sku": "ELEC-HB-003", "description": "USB-C hub with HDMI, USB 3.0, SD card reader", "price": 45.00,  "stock": 200, "cat": "Electronics", "sup": "TechPro Supplies"},
    {"name": "LED Monitor 24\"",        "sku": "ELEC-MN-004", "description": "Full HD IPS display, 75Hz refresh rate", "price": 189.00, "stock": 30,  "cat": "Electronics", "sup": "TechPro Supplies"},
    {"name": "Noise-Cancelling Headset","sku": "ELEC-HS-005", "description": "Over-ear Bluetooth headset with active noise cancellation", "price": 129.99,"stock": 60,  "cat": "Electronics", "sup": "TechPro Supplies"},
    {"name": "Webcam 1080p",            "sku": "ELEC-WC-006", "description": "Full HD webcam with built-in microphone and auto-focus", "price": 59.99,  "stock": 90,  "cat": "Electronics", "sup": "TechPro Supplies"},
    # Clothing
    {"name": "Classic White T-Shirt",   "sku": "CLTH-TS-001", "description": "100% cotton, unisex fit, available S-XXL", "price": 12.99,  "stock": 500, "cat": "Clothing", "sup": "Global Fashion Co"},
    {"name": "Slim Fit Chinos",         "sku": "CLTH-CH-002", "description": "Stretch cotton chinos in khaki and navy", "price": 39.99,  "stock": 250, "cat": "Clothing", "sup": "Global Fashion Co"},
    {"name": "Running Jacket",          "sku": "CLTH-JK-003", "description": "Lightweight windproof running jacket with reflective strips", "price": 54.99,  "stock": 100, "cat": "Clothing", "sup": "Global Fashion Co"},
    {"name": "Sports Sneakers",         "sku": "CLTH-SN-004", "description": "Breathable mesh sneakers for gym and casual wear", "price": 65.00,  "stock": 80,  "cat": "Clothing", "sup": "Global Fashion Co"},
    {"name": "Polo Shirt",              "sku": "CLTH-PL-005", "description": "Pique cotton polo shirt, 8 colors available", "price": 22.99,  "stock": 300, "cat": "Clothing", "sup": "Global Fashion Co"},
    # Food & Beverage
    {"name": "Instant Coffee Mix",      "sku": "FOOD-CF-001", "description": "3-in-1 instant coffee, 20 sachets per box", "price": 5.49,   "stock": 1000,"cat": "Food & Beverage", "sup": "FreshGoods VN"},
    {"name": "Organic Green Tea",       "sku": "FOOD-GT-002", "description": "Premium organic green tea, 50 tea bags", "price": 8.99,   "stock": 600, "cat": "Food & Beverage", "sup": "FreshGoods VN"},
    {"name": "Protein Bar Box",         "sku": "FOOD-PB-003", "description": "High-protein snack bar, 12-pack, chocolate flavour", "price": 24.99,  "stock": 400, "cat": "Food & Beverage", "sup": "FreshGoods VN"},
    {"name": "Sparkling Water 6-Pack",  "sku": "FOOD-SW-004", "description": "Natural mineral sparkling water, 500ml bottles", "price": 4.99,   "stock": 800, "cat": "Food & Beverage", "sup": "FreshGoods VN"},
    # Office Supplies
    {"name": "A4 Copy Paper (500 sheets)","sku":"OFFC-PP-001", "description": "80gsm premium copy paper, ream of 500 sheets", "price": 7.99,   "stock": 2000,"cat": "Office Supplies", "sup": "TechPro Supplies"},
    {"name": "Ballpoint Pen Pack",      "sku": "OFFC-PN-002", "description": "Smooth-writing ballpoint pens, box of 12, blue ink", "price": 3.49,   "stock": 1500,"cat": "Office Supplies", "sup": "TechPro Supplies"},
    {"name": "Desk Organizer",          "sku": "OFFC-DO-003", "description": "Bamboo desk organizer with 5 compartments", "price": 18.99,  "stock": 120, "cat": "Office Supplies", "sup": "TechPro Supplies"},
    {"name": "Sticky Notes Pack",       "sku": "OFFC-SN-004", "description": "Assorted colours sticky notes, 6 pads of 100 sheets", "price": 6.99,   "stock": 700, "cat": "Office Supplies", "sup": "TechPro Supplies"},
    {"name": "Stapler Heavy Duty",      "sku": "OFFC-ST-005", "description": "Heavy-duty stapler, 25 sheet capacity, includes 1000 staples", "price": 14.99,  "stock": 200, "cat": "Office Supplies", "sup": "TechPro Supplies"},
]

ORDER_STATUSES = ["pending", "completed", "completed", "completed", "cancelled"]


# ---------------------------------------------------------------------------
# PostgreSQL seeding
# ---------------------------------------------------------------------------

async def seed_postgres() -> dict[str, dict]:
    """
    Insert categories, suppliers, products.
    Returns mapping: {product_sku: {id, name, price, stock}}
    """
    log.info("=== Seeding PostgreSQL ===")
    conn = await asyncpg.connect(**PG_CONFIG)
    try:
        # Categories
        cat_ids: dict[str, int] = {}
        for cat in CATEGORIES:
            row = await conn.fetchrow(
                """
                INSERT INTO categories (name, description)
                VALUES ($1, $2)
                ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description
                RETURNING id
                """,
                cat["name"], cat["description"],
            )
            cat_ids[cat["name"]] = row["id"]
        log.info(f"  categories: {len(cat_ids)} upserted")

        # Suppliers
        sup_ids: dict[str, int] = {}
        for sup in SUPPLIERS:
            row = await conn.fetchrow(
                """
                INSERT INTO suppliers (name, contact_email, phone)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING
                RETURNING id
                """,
                sup["name"], sup["contact_email"], sup["phone"],
            )
            if row is None:
                # already exists – fetch id
                row = await conn.fetchrow("SELECT id FROM suppliers WHERE name=$1", sup["name"])
            sup_ids[sup["name"]] = row["id"]
        log.info(f"  suppliers: {len(sup_ids)} upserted")

        # Products
        product_map: dict[str, dict] = {}
        for p in PRODUCT_TEMPLATES:
            row = await conn.fetchrow(
                """
                INSERT INTO products (name, sku, description, price, stock, category_id, supplier_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (sku) DO UPDATE
                    SET name=EXCLUDED.name, price=EXCLUDED.price, stock=EXCLUDED.stock
                RETURNING id
                """,
                p["name"], p["sku"], p["description"],
                p["price"], p["stock"],
                cat_ids.get(p["cat"]),
                sup_ids.get(p["sup"]),
            )
            product_map[p["sku"]] = {
                "id":    row["id"],
                "name":  p["name"],
                "price": p["price"],
                "stock": p["stock"],
                "sku":   p["sku"],
            }
        log.info(f"  products: {len(product_map)} upserted")
        return product_map

    finally:
        await conn.close()


# ---------------------------------------------------------------------------
# MySQL seeding
# ---------------------------------------------------------------------------

async def seed_mysql(product_map: dict[str, dict]) -> None:
    """Insert 30 orders with items using products from PostgreSQL."""
    log.info("=== Seeding MySQL ===")
    conn = await aiomysql.connect(**MY_CONFIG)
    try:
        async with conn.cursor() as cur:
            products = list(product_map.values())
            base_date = datetime.now(tz=timezone.utc) - timedelta(days=30)

            for i in range(30):
                # Pick 1-3 random products for this order
                items = random.sample(products, k=random.randint(1, 3))
                total = 0.0
                status = random.choice(ORDER_STATUSES)
                order_date = base_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))

                await cur.execute(
                    """
                    INSERT INTO orders (status, total_amount, notes, created_at)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (status, 0.0, f"Seed order #{i+1}", order_date),
                )
                order_id = cur.lastrowid

                for product in items:
                    qty = random.randint(1, 10)
                    subtotal = round(product["price"] * qty, 2)
                    total += subtotal
                    await cur.execute(
                        """
                        INSERT INTO order_items
                            (order_id, product_id, product_name, quantity, unit_price, subtotal)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (order_id, product["id"], product["name"], qty, product["price"], subtotal),
                    )

                await cur.execute(
                    "UPDATE orders SET total_amount=%s WHERE id=%s",
                    (round(total, 2), order_id),
                )

            await conn.commit()
        log.info("  orders: 30 inserted")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# MongoDB seeding
# ---------------------------------------------------------------------------

async def seed_mongodb(product_map: dict[str, dict]) -> None:
    """Insert ~100 product events with varying structure."""
    log.info("=== Seeding MongoDB ===")

    if MONGO_USER and MONGO_PASS:
        mongo_url = (
            f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"
            f"/{MONGO_DB}?authSource={MONGO_AUTH}"
        )
    else:
        mongo_url = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"

    client = AsyncIOMotorClient(mongo_url)
    db = client[MONGO_DB]
    collection = db["product_events"]

    try:
        events = []
        base_time = datetime.now(tz=timezone.utc) - timedelta(days=30)
        products = list(product_map.values())

        # 1 creation event per product
        for prod in products:
            events.append({
                "product_id": prod["id"],
                "event_type": "product_created",
                "timestamp":  base_time + timedelta(days=random.randint(0, 2)),
                "metadata": {
                    "name":  prod["name"],
                    "price": prod["price"],
                    "stock": prod["stock"],
                    "sku":   prod["sku"],
                },
            })

        # Random update events to reach ~100 total
        event_types = [
            "price_changed",
            "stock_updated",
            "product_updated",
        ]
        remaining = 100 - len(products)
        for _ in range(remaining):
            prod = random.choice(products)
            etype = random.choice(event_types)
            ts = base_time + timedelta(
                days=random.randint(2, 28),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            if etype == "price_changed":
                old_price = prod["price"]
                new_price = round(old_price * random.uniform(0.85, 1.25), 2)
                meta = {"old_price": old_price, "new_price": new_price}
            elif etype == "stock_updated":
                old_stock = prod["stock"]
                delta = random.randint(-20, 50)
                new_stock = max(0, old_stock + delta)
                meta = {
                    "old_stock": old_stock,
                    "new_stock": new_stock,
                    "delta": delta,
                    "reason": random.choice(["warehouse_restock", "sale", "adjustment", "return"]),
                }
            else:
                meta = {"changed_fields": random.sample(["description", "name", "sku"], k=1)}

            events.append({
                "product_id": prod["id"],
                "event_type": etype,
                "timestamp":  ts,
                "metadata":   meta,
            })

        # Sort chronologically before insert
        events.sort(key=lambda e: e["timestamp"])

        # Clear existing seed data and re-insert
        await collection.delete_many({"metadata.seeded": True})
        for ev in events:
            ev["metadata"]["seeded"] = True

        result = await collection.insert_many(events)
        log.info(f"  product_events: {len(result.inserted_ids)} inserted")

        # Ensure indexes
        await collection.create_index([("product_id", 1), ("timestamp", -1)])
        await collection.create_index([("timestamp", -1)])
        log.info("  indexes ensured")

    finally:
        client.close()


# ---------------------------------------------------------------------------
# Redis cache warming
# ---------------------------------------------------------------------------

async def seed_redis(product_map: dict[str, dict]) -> None:
    """Warm cache for the first 5 products."""
    log.info("=== Seeding Redis ===")
    try:
        r = aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASS,
            db=REDIS_DB,
            decode_responses=True,
        )
        await r.ping()

        products = list(product_map.values())[:5]
        for prod in products:
            key = f"product:{prod['id']}"
            await r.set(key, json.dumps(prod), ex=CACHE_TTL)
            log.info(f"  cached {key}")

        await r.close()
        log.info(f"  Redis cache warmed for {len(products)} products")
    except Exception as exc:
        log.warning(f"  Redis unavailable (skipping): {exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    log.info("Starting seed process...")

    # PostgreSQL must run first – other seeders depend on product IDs
    product_map = await seed_postgres()

    # MySQL and MongoDB can run in parallel
    await asyncio.gather(
        seed_mysql(product_map),
        seed_mongodb(product_map),
    )

    # Redis last (optional, non-critical)
    await seed_redis(product_map)

    log.info("✅  Seed complete!")


if __name__ == "__main__":
    asyncio.run(main())
