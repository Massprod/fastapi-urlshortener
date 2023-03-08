from pydantic import BaseModel
from typing import Optional


class RandomShort(BaseModel):
    origin_url: str = "https://www.pythonanywhere.com/"
    short_length: int = 1


class RandomShortResponse(BaseModel):
    origin_url: str
    rshort_url: Optional[str] = None

