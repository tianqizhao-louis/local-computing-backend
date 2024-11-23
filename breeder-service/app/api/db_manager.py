import httpx
import logging
from app.api.models import BreederIn, PetIn
from app.api.db import breeders, database
from typing import Optional

PET_SERVICE_URL = "http://localhost:8082/api/v1/pets"  # Replace with your actual pet service URL
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def add_breeder(payload: BreederIn, breeder_id: str):
    query = breeders.insert().values(id=breeder_id, **payload.model_dump())
    return await database.execute(query=query)

async def get_all_breeders(
    breeder_city: Optional[str], limit: Optional[int], offset: Optional[int]
):
    query = breeders.select()
    if breeder_city:
        query = query.where(breeders.c.breeder_city == breeder_city)
    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)
    return await database.fetch_all(query)

async def get_breeder(id: str):
    query = breeders.select().where(breeders.c.id == id)
    return await database.fetch_one(query=query)

async def delete_breeder(id: str):
    query = breeders.delete().where(breeders.c.id == id)
    return await database.execute(query=query)

async def update_breeder(id: str, payload: BreederIn):
    query = breeders.update().where(breeders.c.id == id).values(**payload.model_dump())
    return await database.execute(query=query)

async def delete_all_breeders():
    query = breeders.delete()
    return await database.execute(query=query)

async def get_breeder_by_email(email: str):
    query = breeders.select().where(breeders.c.email == email)
    return await database.fetch_one(query=query)


async def add_pet(payload: PetIn, breeder_id: str, pet_id: str):
    async with httpx.AsyncClient() as client:
        data = {
            "id": pet_id,
            "breeder_id": breeder_id,
            "name": payload.name,
            "type": payload.type,
            "price": payload.price,
            "image_url": payload.image_url,
        }
        url = f"{PET_SERVICE_URL}/"
        
        # Detailed logging for the request
        logging.info(f"Sending POST request to {url} with payload: {data}")

        try:
            response = await client.post(url, json=data)

            # Log response status and content
            logging.info(f"Received response: status_code={response.status_code}, response_body={response.text}")

            response.raise_for_status()  # Raise exception if response status is 4xx or 5xx
        except httpx.HTTPStatusError as http_err:
            logging.error(f"HTTP error occurred: status_code={http_err.response.status_code}, response_body={http_err.response.text}")
            raise Exception(f"Failed to add pet: {http_err.response.text}")
        except Exception as err:
            logging.error(f"An unexpected error occurred: {str(err)}")
            raise Exception(f"Failed to add pet: {str(err)}")

        # Return the response JSON if successful
        return response.json()


async def get_pets_for_breeder(breeder_id: str):
    async with httpx.AsyncClient() as client:
        url = f"{PET_SERVICE_URL}/breeder/{breeder_id}/"
        
        # Detailed logging for the request
        logging.info(f"Sending GET request to {url}")

        try:
            response = await client.get(url)

            # Log response status and content
            logging.info(f"Received response: status_code={response.status_code}, response_body={response.text}")

            response.raise_for_status()  # Raise exception if response status is 4xx or 5xx
        except httpx.HTTPStatusError as http_err:
            logging.error(f"HTTP error occurred: status_code={http_err.response.status_code}, response_body={http_err.response.text}")
            raise Exception(f"Failed to fetch pets for breeder: {http_err.response.text}")
        except Exception as err:
            logging.error(f"An unexpected error occurred: {str(err)}")
            raise Exception(f"Failed to fetch pets for breeder: {str(err)}")

        # Return the response JSON if successful
        return response.json()
