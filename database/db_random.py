import random
import string
from schemas.schemas import RandomShortResponse, RandomShort
from sqlalchemy.orm.session import Session
from fastapi import Request, HTTPException, status
from database.models import DbRandom
import requests


def create_rshort(length: int = 4) -> str:
    if length <= 3 or length >= 11:
        raise AttributeError("Length should be from 4 to 10")
    short = "".join(random.choices(string.ascii_letters + string.digits, k=length))
    return short


def working_url(url: str, timeout: int = 4) -> bool:
    try:
        if requests.head(url, timeout=timeout).status_code <= 400:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False


def create_new_random(req: Request, data: RandomShort, db: Session):
    if not working_url(data.origin_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provided URL not responding")
    while True:
        try:
            short_url = req.base_url.url + create_rshort(data.short_length)
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Length should be from 4 to 10")
        new_short = DbRandom(origin_url=data.origin_url,
                             rshort_url=short_url)
        db.add(new_short)
        db.commit()
        db.refresh(new_short)
        return RandomShortResponse(origin_url=new_short.origin_url, rshort_url=new_short.rshort_url)