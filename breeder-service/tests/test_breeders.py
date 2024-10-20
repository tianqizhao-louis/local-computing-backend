# # tests/test_breeders.py
# import pytest
# from fastapi import FastAPI
# from fastapi.testclient import TestClient
# import os
# from app.api.breeders import breeders
# from app.api.db_manager import database as prod_database
# from tests.test_db import database, metadata, engine

# # Override the production database with our test database
# from app.api import db_manager
# db_manager.database = database

# # Create a test app
# app = FastAPI()
# app.include_router(breeders, prefix="/api/v1/breeders", tags=["breeders"])

# # Create test client
# client = TestClient(app)

# @pytest.fixture(autouse=True)
# async def setup_test_db():
#     # Create tables and connect to test database
#     metadata.create_all(engine)
#     await database.connect()
    
#     yield
    
#     # Cleanup: disconnect and drop tables
#     await database.disconnect()
#     metadata.drop_all(engine)

# def test_create_breeder():
#     """Test creating a new breeder"""
#     test_breeder = {
#         "name": "Test Breeder",
#         "breeder_city": "Test City",
#         "breeder_country": "Test Country",
#         "price_level": "Medium",
#         "breeder_address": "123 Test Street"
#     }
    
#     response = client.post("/api/v1/breeders/", json=test_breeder)
    
#     assert response.status_code == 201
#     data = response.json()
#     assert data["name"] == test_breeder["name"]
#     assert data["breeder_city"] == test_breeder["breeder_city"]
#     assert "id" in data

# def test_get_breeders():
#     """Test getting all breeders"""
#     response = client.get("/api/v1/breeders/")
#     assert response.status_code == 200
