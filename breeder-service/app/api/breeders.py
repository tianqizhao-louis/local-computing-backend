from typing import List, Dict
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    BackgroundTasks,
    Response,
    Request,
)
from app.api.models import (
    BreederOut,
    BreederIn,
    BreederUpdate,
    BreederFilterParams,
    BreederDelayResponse,
    Link,
    BreederListResponse,
    PetIn,
    PetOut,
)
from app.api import db_manager
from app.api.middleware import get_correlation_id, logger
from app.config import settings
import uuid
import os
import httpx

breeders = APIRouter()
bg_tasks: Dict[str, str] = {}
URL_PREFIX = os.getenv("URL_PREFIX")


@breeders.post("/", response_model=BreederOut, status_code=201)
async def create_breeder(payload: BreederIn, response: Response):
    breeder_id = str(uuid.uuid4())
    await db_manager.add_breeder(payload, breeder_id=breeder_id)

    # Add Location header for the created resource
    breeder_url = generate_breeder_url(breeder_id)
    response.headers["Location"] = breeder_url

    # Add Link header for self and collection navigation
    response.headers["Link"] = (
        f'<{breeder_url}>; rel="self", <{URL_PREFIX}/breeders/>; rel="collection"'
    )

    # Include link sections in the response body
    response_data = BreederOut(
        id=breeder_id,
        name=payload.name,
        breeder_city=payload.breeder_city,
        breeder_country=payload.breeder_country,
        price_level=payload.price_level,
        breeder_address=payload.breeder_address,
        email=payload.email,
        links=[
            Link(rel="self", href=breeder_url),
            Link(rel="collection", href=f"{URL_PREFIX}/breeders/"),
        ],
    )
    return response_data


@breeders.post("/delay/", response_model=BreederDelayResponse, status_code=202)
async def create_breeder_delay(
    payload: BreederIn, background_tasks: BackgroundTasks, response: Response
):
    """
    This endpoint is used to simulate a slow response from the server.
    The response status code is 202 (Accepted) to indicate that the request has been
    accepted for processing, but the processing has not been completed yet.
    """
    if all(each_status == "completed" for each_status in bg_tasks.values()):
        bg_tasks.clear()

    breeder_id = str(uuid.uuid4())
    bg_tasks[breeder_id] = "pending"

    # Add the background task to be processed asynchronously
    background_tasks.add_task(process_breeder_task, breeder_id, payload)

    # Generate status URL
    status_url = f"/task-status/{breeder_id}/"

    # Add Link header for status tracking and self navigation
    response.headers["Link"] = f'<{status_url}>; rel="status"'

    # Response with status tracking link
    response_data = BreederDelayResponse(
        name=payload.name,
        breeder_city=payload.breeder_city,
        breeder_country=payload.breeder_country,
        price_level=payload.price_level,
        breeder_address=payload.breeder_address,
        email=payload.email,
        status_url=status_url,
        links=[
            Link(rel="self", href=f"/breeders/{breeder_id}/"),
            Link(rel="status", href=status_url),
        ],
    )
    return response_data


@breeders.post("/{breeder_id}/pets/", response_model=PetOut, status_code=201)
async def add_pet_to_breeder(breeder_id: str, payload: PetIn, request: Request):
    breeder = await db_manager.get_breeder(breeder_id)
    if not breeder:
        raise HTTPException(status_code=404, detail="Breeder not found")

    pet_id = str(uuid.uuid4())  # Generate unique ID for the pet
    try:
        # pet_data = await db_manager.add_pet(payload, breeder_id, pet_id)
        async with httpx.AsyncClient() as client:
            data = {
                "id": pet_id,
                "breeder_id": breeder_id,
                "name": payload.name,
                "type": payload.type,
                "price": payload.price,
                "image_url": payload.image_url,
            }
            url = f"{settings.PET_SERVICE_URL}/"

            # Detailed logging for the request
            logger.info(f"Sending POST request to {url} with payload: {data}")

            headers = {
                "X-Correlation-ID": get_correlation_id(),
                "Authorization": f"{request.headers.get('Authorization')}",
            }

            try:
                response = await client.post(url, json=data, headers=headers)
                logger.info(
                    f"Received response: status_code={response.status_code}, response_body={response.text}"
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as http_err:
                logger.error(
                    f"HTTP error occurred: status_code={http_err.response.status_code}, response_body={http_err.response.text}"
                )
                raise Exception(f"Failed to add pet: {http_err.response.text}")
            except Exception as err:
                logger.error(f"An unexpected error occurred: {str(err)}")
                raise Exception(f"Failed to add pet: {str(err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add pet: {str(e)}")

    pet_url = f"{URL_PREFIX}/breeders/{breeder_id}/pets/{pet_id}"
    response.headers["Location"] = pet_url

    response_data = PetOut(
        id=pet_id,
        breeder_id=breeder_id,
        name=payload.name,
        type=payload.type,
        price=payload.price,
        image_url=payload.image_url,
    )
    return response_data


@breeders.get("/{breeder_id}/pets/", response_model=List[PetOut], status_code=200)
async def get_pets_for_breeder(breeder_id: str, request: Request):
    breeder = await db_manager.get_breeder(breeder_id)
    if not breeder:
        raise HTTPException(status_code=404, detail="Breeder not found")

    try:
        # pets = await db_manager.get_pets_for_breeder(breeder_id)
        async with httpx.AsyncClient() as client:
            url = f"{settings.PET_SERVICE_URL}/breeder/{breeder_id}/"
            logger.info(f"Sending GET request to {url}")
            headers = {
                "X-Correlation-ID": get_correlation_id(),
                "Authorization": f"{request.headers.get('Authorization')}",
            }
            try:
                response = await client.get(url, headers=headers)
                logger.info(
                    f"Received response: status_code={response.status_code}, response_body={response.text}"
                )
                response.raise_for_status()
                pets = response.json()
            except httpx.HTTPStatusError as http_err:
                logger.error(
                    f"HTTP error occurred: status_code={http_err.response.status_code}, response_body={http_err.response.text}"
                )
                raise Exception(
                    f"Failed to fetch pets for breeder: {http_err.response.text}"
                )
            except Exception as err:
                logger.error(f"An unexpected error occurred: {str(err)}")
                raise Exception(f"Failed to fetch pets for breeder: {str(err)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pets: {str(e)}")

    return [
        PetOut(
            id=pet["id"],
            breeder_id=pet["breeder_id"],
            name=pet["name"],
            type=pet["type"],
            price=pet.get("price"),
            image_url=pet.get("image_url"),
        )
        for pet in pets
    ]


@breeders.get("/", response_model=BreederListResponse)
async def get_breeders(params: BreederFilterParams = Depends()):
    cor_id = get_correlation_id()
    logger.info(f"[{cor_id}] Processing root request")
    # Fetching database records
    db_records = await db_manager.get_all_breeders(
        limit=params.limit, offset=params.offset, breeder_city=params.breeder_city
    )

    # Convert each database record to the BreederOut model and add links
    breeders = [
        BreederOut(
            id=record["id"],
            name=record["name"],
            breeder_city=record["breeder_city"],
            breeder_country=record["breeder_country"],
            price_level=record["price_level"],
            breeder_address=record["breeder_address"],
            email=record["email"],
            links=[
                Link(rel="self", href=f"{URL_PREFIX}/breeders/{record['id']}/"),
                Link(rel="collection", href=f"{URL_PREFIX}/breeders/"),
            ],
        )
        for record in db_records
    ]

    # Add Link headers to paginate and return a collection link in response
    links = [
        Link(rel="self", href=f"{URL_PREFIX}/breeders/"),
        Link(rel="collection", href=f"{URL_PREFIX}/breeders/"),
    ]

    if params.limit:
        next_offset = params.offset + params.limit
        links.append(
            Link(
                rel="next",
                href=f"{URL_PREFIX}/breeders/?limit={params.limit}&offset={next_offset}",
            )
        )

    # Return the data with links using the BreederListResponse model
    return BreederListResponse(
        data=breeders,  # List of BreederOut instances
        links=links,  # List of Link instances
    )


@breeders.get("/{id}/", response_model=BreederOut)
async def get_breeder(id: str):
    breeder = await db_manager.get_breeder(id)
    if not breeder:
        raise HTTPException(status_code=404, detail="Breeder not found")

    # Include link to self and collection in the response
    response_data = BreederOut(
        id=breeder["id"],
        name=breeder["name"],
        breeder_city=breeder["breeder_city"],
        breeder_country=breeder["breeder_country"],
        price_level=breeder["price_level"],
        breeder_address=breeder["breeder_address"],
        email=breeder["email"],
        links=[
            Link(rel="self", href=f"{URL_PREFIX}/breeders/{id}/"),
            Link(rel="collection", href=f"{URL_PREFIX}/breeders/"),
        ],
    )
    return response_data


@breeders.put("/{id}/", response_model=BreederOut)
async def update_breeder(id: str, payload: BreederUpdate):
    breeder = await db_manager.get_breeder(id)
    if not breeder:
        raise HTTPException(status_code=404, detail="Breeder not found")

    update_data = payload.model_dump(exclude_unset=True)
    breeder_in_db = BreederIn(**breeder)
    updated_breeder = breeder_in_db.model_copy(update=update_data)

    await db_manager.update_breeder(id, updated_breeder)
    updated_breeder_in_db = await db_manager.get_breeder(id)

    # Include updated response with link sections
    response_data = BreederOut(
        id=updated_breeder_in_db["id"],
        name=updated_breeder_in_db["name"],
        breeder_city=updated_breeder_in_db["breeder_city"],
        breeder_country=updated_breeder_in_db["breeder_country"],
        price_level=updated_breeder_in_db["price_level"],
        breeder_address=updated_breeder_in_db["breeder_address"],
        email=updated_breeder_in_db["email"],
        links=[
            Link(rel="self", href=f"{URL_PREFIX}/breeders/{id}/"),
            Link(rel="collection", href=f"{URL_PREFIX}/breeders/"),
        ],
    )
    return response_data


@breeders.delete("/{id}/", response_model=None, status_code=200)
async def delete_breeder(id: str):
    breeder = await db_manager.get_breeder(id)
    if not breeder:
        raise HTTPException(status_code=404, detail="Breeder not found")
    return await db_manager.delete_breeder(id)


@breeders.delete("/delete/all/", response_model=None, status_code=200)
async def delete_all_breeders():
    """
    This endpoint deletes all breeders from the database.
    """
    try:
        await db_manager.delete_all_breeders()  # Assuming db_manager has this method
        return {"message": "All breeders have been deleted."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete all breeders: {str(e)}"
        )


# Helper function to generate breeder URL
def generate_breeder_url(breeder_id: str):
    return f"{URL_PREFIX}/breeders/{breeder_id}/"


@breeders.get("/email/{email}/", response_model=BreederOut, status_code=200)
async def get_breeder_by_email(email: str):
    breeder = await db_manager.get_breeder_by_email(email)

    if not breeder:
        raise HTTPException(status_code=404, detail="Customer not found")

    response_data = BreederOut(
        id=breeder["id"],
        name=breeder["name"],
        breeder_city=breeder["breeder_city"],
        breeder_country=breeder["breeder_country"],
        price_level=breeder["price_level"],
        breeder_address=breeder["breeder_address"],
        email=breeder["email"],
        links=[
            Link(rel="self", href=f"{URL_PREFIX}/breeders/{breeder['id']}/"),
            Link(rel="collection", href=f"{URL_PREFIX}/breeders/"),
        ],
    )
    return response_data


@breeders.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in bg_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return the current status of the task
    return {"task_id": task_id, "status": bg_tasks[task_id]}


# Non-CRUD operations
async def process_breeder_task(breeder_id: str, payload: BreederIn):
    import asyncio  # Import asyncio for asynchronous sleep

    await asyncio.sleep(30)  # Non-blocking sleep

    await db_manager.add_breeder(payload, breeder_id=breeder_id)
    # Update task status to "completed" after processing
    bg_tasks[breeder_id] = "completed"


# Helper function to generate breeder URL
def generate_breeder_url(breeder_id: str):
    return f"/breeders/{breeder_id}/"


# To propagate the correlation ID to external services, include it in your HTTP client headers:
# pythonCopyimport httpx
# from .middleware import get_correlation_id

# async def call_external_service():
#     headers = {"X-Correlation-ID": get_correlation_id()}
#     async with httpx.AsyncClient() as client:
#         response = await client.get("https://api.example.com", headers=headers)
#     return response
