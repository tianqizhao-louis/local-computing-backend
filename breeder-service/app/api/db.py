import os

from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table,
                        create_engine, ARRAY)

from databases import Database

DATABASE_URI = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URI)
metadata = MetaData()

breeders = Table(
    'breeders',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
)

database = Database(DATABASE_URI)