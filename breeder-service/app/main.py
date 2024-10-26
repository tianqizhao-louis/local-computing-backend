from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.breeders import breeders
from app.api.db import metadata, database, engine
from app.api.middleware import LoggingMiddleware
from contextlib import asynccontextmanager

from sqlalchemy.exc import IntegrityError

import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code: connect to the database
    await database.connect()
    yield
    # Shutdown code: disconnect from the database
    await database.disconnect()

if os.getenv("FASTAPI_ENV") == "production":
    try:
        metadata.create_all(engine)
    except IntegrityError as e:
        print(f"Database already initialized: {e}")
else:
    metadata.drop_all(engine)
    metadata.create_all(engine)


# # Check if the environment is set to production
# if os.getenv("FASTAPI_ENV") == "production":
#     try:
#         metadata.drop_all(engine)  # Clears existing tables
#         metadata.create_all(engine)  # Recreates tables
#         print("Database tables dropped and recreated for production.")
#     except IntegrityError as e:
#         print(f"An error occurred during database initialization: {e}")
# else:
#     metadata.create_all(engine)


app = FastAPI(
    openapi_url="/api/v1/breeders/openapi.json",
    docs_url="/api/v1/breeders/docs",
    lifespan=lifespan,  # Use lifespan event handler
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://34.120.15.105",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(breeders, prefix="/api/v1/breeders", tags=["breeders"])
