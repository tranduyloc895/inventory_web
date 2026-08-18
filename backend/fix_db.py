import asyncio
from sqlalchemy import text
from app.database.mysql import engine

async def main():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE products ADD COLUMN owner_id INT;"))
            print("Successfully added owner_id column to products table!")
        except Exception as e:
            print(f"Error (maybe column already exists): {e}")

if __name__ == "__main__":
    asyncio.run(main())
