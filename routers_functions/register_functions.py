from fastapi import Request, HTTPException, status
from sqlalchemy.orm.session import Session
from schemas.schemas import NewKey, ActivateResponse
from routers_functions.scope_all import create_send_key
from database.models import DbKeys


def add_new_key(req: Request, data: NewKey, db: Session):
    key = data.api_key.strip(" ")
    activation_link = req.base_url.url + "activate/" + key
    send = create_send_key(data.email, activation_link, key)
    if send:
        new_key = DbKeys(api_key=key,
                         email=data.email,
                         activation_link=activation_link,
                         link_send=True,
                         activated=False
                         )
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        return new_key
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Provided Email incorrect or unreachable")


def activate_new_key(req: Request, activation_key: str, db: Session):
    activation_link = req.base_url.url + "activate/" + activation_key
    if exist := db.query(DbKeys).filter_by(activation_link=activation_link).first():
        act_row = db.query(DbKeys).get(exist.api_key)
        act_row.activation_link = "used"
        act_row.activated = True
        db.commit()
        return act_row
