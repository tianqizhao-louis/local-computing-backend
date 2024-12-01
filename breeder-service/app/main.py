from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.breeders import breeders
from app.api.db import metadata, database, engine, initialize_database, cleanup
from app.api.middleware import LoggingMiddleware
from contextlib import asynccontextmanager
from gcloud.aio.pubsub import PublisherClient, SubscriberClient, PubsubMessage
from app.api import db_manager
from app.api.auth import auth
from app.api.middleware import JWTMiddleware

import asyncio
import json
import os
import logging


@asynccontextmanager
async def lifespan(app):
    # Initialize the database connection
    await initialize_database()

    # Set up Pub/Sub configurations
    project_name = os.getenv("GCP_PROJECT_ID")
    request_subscription_name = os.getenv("REQUEST_SUBSCRIPTION_NAME")
    response_topic = os.getenv("RESPONSE_TOPIC")
    response_topic_name = f"projects/{project_name}/topics/{response_topic}"
    subscription_name = (
        f"projects/{project_name}/subscriptions/{request_subscription_name}"
    )

    # Define an async function to process incoming Pub/Sub messages
    async def process_pubsub_messages():
        async with SubscriberClient() as subscriber, PublisherClient() as publisher:
            while True:
                try:
                    # Pull messages from the subscription
                    messages = await subscriber.pull(subscription_name, max_messages=10)
                    for msg in messages:
                        try:
                            # Parse the message
                            message_data = json.loads(msg.data.decode("utf-8"))
                            breeder_id = message_data.get("breeder_id")
                            correlation_id = message_data.get("correlation_id")

                            if not breeder_id or not correlation_id:
                                logging.warning(
                                    f"Message missing required fields: {msg.data}"
                                )
                                await subscriber.acknowledge(
                                    subscription_name, [msg.ack_id]
                                )
                                continue

                            # Fetch breeder details from the database
                            breeder = await db_manager.get_breeder(breeder_id)

                            if not breeder:
                                logging.warning(
                                    f"Breeder with ID {breeder_id} not found"
                                )
                                response_message = {
                                    "correlation_id": correlation_id,
                                    "error": "Breeder not found",
                                }
                            else:
                                # Prepare response with breeder details
                                response_message = {
                                    "correlation_id": correlation_id,
                                    "breeder_data": {
                                        "id": breeder["id"],
                                        "name": breeder["name"],
                                        "breeder_city": breeder["breeder_city"],
                                        "breeder_country": breeder["breeder_country"],
                                        "price_level": breeder["price_level"],
                                        "breeder_address": breeder["breeder_address"],
                                        "email": breeder["email"],
                                    },
                                }

                            # Publish the response to the response topic
                            response_data = json.dumps(response_message).encode("utf-8")
                            pubsub_message = PubsubMessage(data=response_data)
                            await publisher.publish(
                                response_topic_name, [pubsub_message]
                            )

                            # Acknowledge the original message
                            await subscriber.acknowledge(
                                subscription_name, [msg.ack_id]
                            )

                        except Exception as e:
                            logging.error(f"Error processing message: {e}")
                            continue

                except Exception as e:
                    logging.error(f"Error in Pub/Sub message loop: {e}")
                    await asyncio.sleep(5)  # Delay to prevent tight error loops

    # Start the Pub/Sub message processor as a background task
    pubsub_task = asyncio.create_task(process_pubsub_messages())

    yield  # Control is handed over to FastAPI for request handling

    # Cleanup code on shutdown
    pubsub_task.cancel()
    try:
        await pubsub_task
    except asyncio.CancelledError:
        pass

    # Close the database connection
    await cleanup()


app = FastAPI(
    openapi_url="/api/v1/breeders/openapi.json",
    docs_url="/api/v1/breeders/docs",
    lifespan=lifespan,  # Use lifespan event handler
)

origins = [
    "*",
    # "http://localhost",
    # "http://localhost:3000",
    # "http://34.29.2.129",
    # "http://35.193.234.242",
    # "http://34.29.2.129:3000", # UI IPv4
    # "http://35.193.234.242:8004", #Composite IPv4
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(JWTMiddleware, excluded_paths=["/api/v1/auth"])

app.include_router(breeders, prefix="/api/v1/breeders", tags=["breeders"])
app.include_router(auth, prefix="/api/v1/auth", tags=["auth"])
