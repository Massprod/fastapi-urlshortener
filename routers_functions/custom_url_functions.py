from fastapi import Request, status, HTTPException
from sqlalchemy.orm import Session
from schemas.schemas import CustomShort, CustomShortResponse
from database.models import DbCustom, DbKeys
from routers_functions.scope_all import working_url, expire_date, del_expired


def create_new_custom(req: Request, data: CustomShort, db: Session, api_key: str = None) -> CustomShortResponse:
    expire_limit = 0 < data.expire_days <= 10
    expire_limit_with_key = 0 < data.expire_days <= 30

    try:
        api_key_active = db.query(DbKeys).filter_by(api_key=api_key).first().activated
    except AttributeError:
        api_key_active = False

    if len(data.custom_name) == 0 or len(data.custom_name) > 30:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Custom name can't be empty STRING and longer than 30 symbols")
    elif not expire_limit and not api_key_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Expire days limited to 10")
    elif not working_url(data.origin_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provided URL not responding or incorrect")

    new_custom = req.base_url.url + data.custom_name.strip(" ")
    del_expired(db_model=DbCustom, db=db, del_one_short=new_custom)
    if exist := db.query(DbCustom).filter_by(short_url=new_custom).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Custom name already used: '{exist.short_url}'")
    elif not expire_limit_with_key and api_key_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Expire days for api_key limited to 30")
    new_custom = DbCustom(
        origin_url=data.origin_url,
        short_url=new_custom,
        api_key=api_key,
        expire_date=expire_date(data.expire_days),
    )
    db.add(new_custom)
    db.commit()
    db.refresh(new_custom)
    return new_custom
