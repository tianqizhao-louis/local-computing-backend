from pydantic import BaseModel
from typing import List, Optional

class BreederIn(BaseModel):
    name: str


class BreederOut(BreederIn):
    id: int


# class MovieUpdate(MovieIn):
#     name: Optional[str] = None
#     plot: Optional[str] = None
#     genres: Optional[List[str]] = None
#     casts_id: Optional[List[int]] = None