from app.api.models import BreederIn, BreederOut
from app.api.db import breeders, database


async def add_breeder(payload: BreederIn):
    query = breeders.insert().values(**payload.dict())

    return await database.execute(query=query)

async def get_all_breeders():
    query = breeders.select()
    return await database.fetch_all(query=query)

# async def get_movie(id):
#     query = movies.select(movies.c.id==id)
#     return await database.fetch_one(query=query)

# async def delete_movie(id: int):
#     query = movies.delete().where(movies.c.id==id)
#     return await database.execute(query=query)

# async def update_movie(id: int, payload: MovieIn):
#     query = (
#         movies
#         .update()
#         .where(movies.c.id == id)
#         .values(**payload.dict())
#     )
#     return await database.execute(query=query)