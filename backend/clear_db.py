import asyncio
from sqlalchemy import text
from app.database.mysql import engine as mysql_engine
from app.database.postgres import engine as pg_engine

async def clear_data():
    print("Clearing MySQL data (Products, Categories, Suppliers)...")
    async with mysql_engine.begin() as conn:
        # Disable foreign key checks temporarily to TRUNCATE
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        await conn.execute(text("TRUNCATE TABLE products;"))
        await conn.execute(text("TRUNCATE TABLE categories;"))
        await conn.execute(text("TRUNCATE TABLE suppliers;"))
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        print("MySQL data cleared.")

    print("Clearing PostgreSQL data (Orders, Order Items)...")
    async with pg_engine.begin() as conn:
        # TRUNCATE CASCADE to handle order_items automatically
        await conn.execute(text("TRUNCATE TABLE orders CASCADE;"))
        print("PostgreSQL data cleared.")
        
    print("All test data has been successfully cleared!")

if __name__ == "__main__":
    asyncio.run(clear_data())
