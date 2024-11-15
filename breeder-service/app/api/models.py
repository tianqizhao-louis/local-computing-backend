from pydantic import BaseModel
from typing import List, Optional


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
    # Add links field to support the HATEOAS concept
    links: Optional[List[Link]] = None


class BreederUpdate(BaseModel):
    # Allow partial updates with optional fields
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
    # Add links field for HATEOAS support
    links: Optional[List[Link]] = None
    email: str


class BreederListResponse(BaseModel):
    data: List[BreederOut]
    links: Optional[List[Link]] = None
