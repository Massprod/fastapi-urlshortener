from schemas.schemas import RandomShortResponse, RandomShort
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from fastapi import Request, HTTPException, status
from database.models import DbShort
from routers_functions.scope_all import working_url, expire_date, create_rshort, del_expired, check_records_count
from math import factorial


def create_new_random(request: Request, data: RandomShort, db: Session) -> RandomShortResponse:
    """Creating Random short Url Db record with provided length"""
    if not working_url(data.origin_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provided Url not responding or incorrect")
    set_length = data.short_length
    records_limit = factorial(62) / factorial(62 - set_length)
    records_count = 0
    while records_limit > records_count:
        try:
            short_url = str(request.base_url) + create_rshort(set_length)
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Length limited from 1 to 10")
        try:
            del_expired(db_model=DbShort, db=db, del_one_short=short_url)
            new_short = DbShort(origin_url=data.origin_url,
                                short_url=short_url,
                                expire_date=expire_date(days=7, seconds=0),
                                length=set_length,
                                )
            db.add(new_short)
            db.commit()
            db.refresh(new_short)
            return new_short
        except IntegrityError:
            db.rollback()
            records_count = check_records_count(db=db, db_model=DbShort, length=set_length)
    raise HTTPException(status_code=status.HTTP_508_LOOP_DETECTED,
                        detail="Can't create short_combination. Might be out of it for this length.")
