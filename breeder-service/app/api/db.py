import os
import uuid
import asyncio
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    ARRAY,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from databases import Database

DATABASE_URI = os.getenv("DATABASE_URI")

# Convert SQLAlchemy URI to async format if needed
if DATABASE_URI.startswith("postgresql://"):
    DATABASE_URI = DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with unique prepared statement names
engine = create_async_engine(
    DATABASE_URI,
    connect_args={
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
)

metadata = MetaData()

breeders = Table(
    "breeders",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("name", String(50)),
    Column("email", String(100)),
    Column("breeder_city", String(100)),
    Column("breeder_country", String(100)),
    Column("price_level", String(50)),
    Column("breeder_address", String(255)),
)

# Setup databases instance with the same connection parameters
database = Database(
    DATABASE_URI,
    min_size=1,
    max_size=10,
    force_rollback=False,
    ssl=None,
    statement_cache_size=0,
)

# Create tables asynchronously
async def create_tables():
    async with engine.begin() as conn:
        if os.getenv("FASTAPI_ENV") == "production":
            # Create table if it doesn't exist
            await conn.run_sync(metadata.create_all, checkfirst=True)
        else:
            # Drop table if it exists, then create it again
            await conn.run_sync(metadata.drop_all)
            await conn.run_sync(metadata.create_all)

# Database setup function
async def setup_database():
    await database.connect()
    await create_tables()

# Function to initialize database (call this in your startup event)
async def initialize_database():
    try:
        await setup_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

# Cleanup function (call this in your shutdown event)
async def cleanup():
    await database.disconnect()

# If you need to create tables from command line
if __name__ == "__main__":
    asyncio.run(create_tables())
