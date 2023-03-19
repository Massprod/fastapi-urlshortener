from fastapi import Request, HTTPException, status
from database.models import DbKeys
from sqlalchemy.orm.session import Session
from schemas.schemas import NewKey, NewKeyResponse, ActivateResponse
from routers_functions.scope_all import create_send_key, create_rshort, expire_date, del_expired
from datetime import datetime as dt


def add_new_key(request: Request, data: NewKey, db: Session) -> NewKeyResponse:
    """Creating new Api-key and sending activation email"""
    email = data.email.replace(" ", "")
    username = data.username.replace(" ", "")
    if len(username) == 0:
        raise HTTPException(status_code=400,
                            detail="Username can't be empty")
    email_expired = del_expired(db_model=DbKeys, db=db, email=email)
    username_expired = del_expired(db_model=DbKeys, db=db, username=username)
    if email_expired is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Email already used: {email}")
    elif username_expired is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Username already used: {username}")
    while True:
        api_key = create_rshort(length=9)
        used = db.query(DbKeys).filter_by(api_key=api_key).first()
        if not used:
            break
    while True:
        activation_key = create_rshort(length=10)
        activation_link = str(request.base_url) + "register/activate/" + activation_key
        used = db.query(DbKeys).filter_by(activation_link=activation_link).first()
        if not used:
            break
    send = create_send_key(email, activation_link, api_key)
    if send:
        new_key = DbKeys(email=email,
                         username=username,
                         api_key=api_key,
                         activation_link=activation_link,
                         link_send=True,
                         activated=False,
                         expire_date=expire_date(days=1, seconds=0)
                         )
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        return new_key
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email empty or incorrect")


def activate_new_key(request: Request, activation_key: str, db: Session) -> ActivateResponse:
    """Checking existence of Activation link in Db and changing it status if Activated"""
    activation_link = str(request.base_url) + "register/" + "activate/" + activation_key.replace(" ", "")
    if exist := db.query(DbKeys).filter_by(activation_link=activation_link).first():
        act_entity = db.get(DbKeys, exist.email)
        act_entity.activation_link = f"key: {activation_key} " \
                                     f"used: {dt.strftime(dt.utcnow(), '%Y.%m.%d')}"
        act_entity.activated = True
        act_entity.expire_date = None
        db.commit()
        db.refresh(act_entity)
        return ActivateResponse(email=act_entity.email,
                                username=act_entity.username,
                                api_key=act_entity.api_key,
                                activated=act_entity.activated
                                )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Link not found. Already Activated or Expired")
