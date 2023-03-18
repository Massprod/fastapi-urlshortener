from fastapi import Request, status, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from schemas.schemas import CustomShort, CustomShortResponse, ShowAllResponse, DeleteCustomResponse
from database.models import DbKeys, DbShort
from routers_functions.scope_all import working_url, expire_date, del_expired
from datetime import datetime


def create_new_custom(request: Request, data: CustomShort, db: Session, api_key: str = None) -> CustomShortResponse:
    """Creating new custom Url for provided Api-key"""
    expire_limit = 0 < data.expire_days <= 10
    expire_limit_with_key = 0 < data.expire_days <= 30
    custom_name = data.custom_name.replace(" ", "")
    if api_key is not None:
        api_key = api_key.replace(" ", "")
    try:
        api_key_active = db.query(DbKeys).filter_by(api_key=api_key).first().activated
    except AttributeError:
        api_key_active = False
        api_key = None
    if len(custom_name) == 0 or len(custom_name) > 30:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Custom name can't be empty String and longer than 30 symbols")
    elif not expire_limit and not api_key_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Expire days limited to 10, can't be Negative. Use Api-key to expend")
    elif not working_url(data.origin_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provided Url not responding or incorrect")
    new_custom = request.base_url.url + custom_name
    del_expired(db_model=DbShort, db=db, del_one_short=new_custom)
    if exist := db.query(DbShort).filter_by(short_url=new_custom).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Custom name already used: '{exist.short_url}'")
    elif not expire_limit_with_key and api_key_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Expire days for Api_key limited to 30, can't be Negative")
    new_custom = DbShort(origin_url=data.origin_url,
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


def delete_by_api_key(request: Request, custom_name: str, api_key: str, db: Session) -> DeleteCustomResponse:
    """Deletes custom_short from Db by its name, if it's associated with given Api-key"""
    if key_exist := db.query(DbKeys).filter_by(api_key=api_key).first():
        if key_exist.activated:
            chosen_url = request.base_url.url + custom_name.replace(" ", "")
            if to_delete := db.query(DbShort).filter_by(short_url=chosen_url).first():
                if to_delete.api_key == key_exist.api_key:
                    db.delete(to_delete)
                    db.commit()
                    return DeleteCustomResponse(origin_url=to_delete.origin_url,
                                                short_url=to_delete.short_url,
                                                api_key=to_delete.api_key,
                                                call_time=datetime.utcnow()
                                                )
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail=f"short Url with custom name: '{custom_name} '"
                                           f"not created by used api-key '{api_key}'")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"short Url with custom name: '{custom_name}' doesn't  exist ")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Api key not Activated")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No such Api-key: {api_key}")
