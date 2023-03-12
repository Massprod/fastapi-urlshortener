from fastapi import Request, status, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from schemas.schemas import CustomShort, CustomShortResponse, ShowAllResponse
from database.models import DbCustom, DbKeys
from routers_functions.scope_all import working_url, expire_date, del_expired


def create_new_custom(req: Request, data: CustomShort, db: Session, api_key: str = None) -> CustomShortResponse:
    """Creating new custom Url for provided Api-key"""
    expire_limit = 0 < data.expire_days <= 10
    expire_limit_with_key = 0 < data.expire_days <= 30
    if api_key is not None:
        api_key = api_key.replace(" ", "")
    try:
        api_key_active = db.query(DbKeys).filter_by(api_key=api_key).first().activated
    except AttributeError:
        api_key_active = False

    if len(data.custom_name) == 0 or len(data.custom_name) > 30:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Custom name can't be empty String and longer than 30 symbols")
    elif not expire_limit and not api_key_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Expire days limited to 10")
    elif not working_url(data.origin_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provided Url not responding or incorrect")

    new_custom = req.base_url.url + data.custom_name.replace(" ", "")
    del_expired(db_model=DbCustom, db=db, del_one_short=new_custom)
    if exist := db.query(DbCustom).filter_by(short_url=new_custom).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Custom name already used: '{exist.short_url}'")
    elif not expire_limit_with_key and api_key_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Expire days for Api_key limited to 30")
    new_custom = DbCustom(
        origin_url=data.origin_url,
        short_url=new_custom,
        api_key=api_key,
        expire_date=expire_date(days=data.expire_days, seconds=0),
    )
    db.add(new_custom)
    db.commit()
    db.refresh(new_custom)
    return new_custom


def show_all_email_customs(identifier: str, db: Session) -> ShowAllResponse:
    """Returns Json with all custom urls created by provided Identifier: Email, Api-key, Username"""
    identifier = identifier.replace(" ", "")
    custom_urls = db.query(DbKeys).filter(or_(DbKeys.email == identifier,
                                              DbKeys.username == identifier,
                                              DbKeys.api_key == identifier)).first()
    if not custom_urls:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Unique Identifier not found. Check for typos or Registrate")
    elif not custom_urls.activated:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Api-key not activated")
    return ShowAllResponse(email=custom_urls.email, custom_urls=custom_urls.custom_urls)
