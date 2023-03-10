from fastapi import Request, status, HTTPException
from sqlalchemy.orm import Session
from schemas.schemas import CustomShort, CustomShortResponse
from database.models import DbCustom
from routers_functions.scope_all import working_url, expire_date


def create_new_custom(req: Request, data: CustomShort, db: Session, api_key: str = None) -> CustomShortResponse:
    if len(data.custom_name) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Custom name can't be empty STRING")
    if not working_url(data.origin_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provided URL not responding or incorrect")
    new_custom = req.base_url.url + data.custom_name.strip(" ")
    if exist := db.query(DbCustom).filter_by(custom_url=new_custom).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Custom name already used: '{exist.custom_url}'")
    new_custom = DbCustom(
        origin_url=data.origin_url,
        custom_url=new_custom,
        api_key=api_key,
        expire_date=expire_date(days=10),
    )
    db.add(new_custom)
    db.commit()
    db.refresh(new_custom)
    return new_custom
