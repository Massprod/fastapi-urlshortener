from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional


class RandomShort(BaseModel):
    origin_url: str = "https://www.pythonanywhere.com/"
    short_length: int = 3


class RandomShortResponse(BaseModel):
    origin_url: str = "https://www.pythonanywhere.com/"
    rshort_url: str = "https://hosting_name/mFh"
    expire_date: datetime = datetime.utcnow() + timedelta(days=7)

    class Config:
        orm_mode = True


class CustomShort(BaseModel):
    origin_url: str = "https://github.com/Massprod/UdemyFastAPI"
    custom_name: str = "provision"


class CustomShortResponse(BaseModel):
    origin_url: str = "https://github.com/Massprod/UdemyFastAPI"
    custom_url: str = "https://hosting_name/provision"
    expire_date: datetime = datetime.utcnow() + timedelta(days=7)

    class Config:
        orm_mode = True


class NewKey(BaseModel):
    email: str = "piankovpe@gmail.com"
    api_key: str = "Will be generate automatically if not provided"


class NewKeyResponse(BaseModel):
    email: str = "piankovpe@gmail.com"
    send: bool = True
    api_key: str = "generated/provided key"

    class Config:
        orm_mode = True


class ActivateResponse(BaseModel):
    api_key: str
    email: str
    activated: bool

    class Config:
        orm_mode = True