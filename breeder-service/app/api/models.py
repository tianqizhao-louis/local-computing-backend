from pydantic import BaseModel
from typing import List, Optional

# Existing models

# Model to represent a hypermedia link
class Link(BaseModel):
    rel: str
    href: str


class BreederIn(BaseModel):
    name: str
    breeder_city: str
    breeder_country: str
    price_level: str
    breeder_address: str
    email: str


class BreederOut(BreederIn):
    id: str
    links: Optional[List[Link]] = None


class BreederUpdate(BaseModel):
    name: Optional[str] = None
    breeder_city: Optional[str] = None
    breeder_country: Optional[str] = None
    price_level: Optional[str] = None
    breeder_address: Optional[str] = None
    email: Optional[str] = None


class BreederFilterParams(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None
    breeder_city: Optional[str] = None


class BreederDelayResponse(BaseModel):
    name: str
    breeder_city: str
    breeder_country: str
    price_level: str
    breeder_address: str
    status_url: str
    links: Optional[List[Link]] = None
    email: str


class BreederListResponse(BaseModel):
    data: List[BreederOut]
    links: Optional[List[Link]] = None

# New models for Pets

class PetIn(BaseModel):
    name: str
    type: str
    price: Optional[float] = None
    image_url: Optional[str] = None

class PetOut(PetIn):
    id: str
    breeder_id: str

