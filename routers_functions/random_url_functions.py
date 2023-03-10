from schemas.schemas import RandomShortResponse, RandomShort
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from fastapi import Request, HTTPException, status
from database.models import DbRandom
from routers_functions.scope_all import working_url, expire_date, create_rshort, is_expired


def create_new_random(req: Request, data: RandomShort, db: Session) -> RandomShortResponse:
    is_expired(db_model=DbRandom, db=db)
    if not working_url(data.origin_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provided URL not responding or incorrect")
    while True:
        try:
            short_url = req.base_url.url + create_rshort(data.short_length)
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Length limited from 3 to 10")
        try:
            new_short = DbRandom(origin_url=data.origin_url,
                                 rshort_url=short_url,
                                 expire_date=expire_date(days=0, seconds=10)
                                 )
            db.add(new_short)
            db.commit()
            db.refresh(new_short)
            return new_short
        except IntegrityError:
            db.rollback()
