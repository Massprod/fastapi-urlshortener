from fastapi import APIRouter, Request, Depends, Path
from sqlalchemy.orm.session import Session
from schemas.schemas import NewKey, NewKeyResponse, ActivateResponse
from database.database import db_session
from routers_functions.register_functions import add_new_key, activate_new_key

register_route = APIRouter(prefix="/register",
                           tags=["register"],
                           )


@register_route.post("/new",
                     response_model=NewKeyResponse,
                     )
def register_new_key(req: Request, data: NewKey, db: Session = Depends(db_session)):
    return add_new_key(req, data, db)


@register_route.get("/activate/{activation_key}",
                    response_model=ActivateResponse,
                    )
def activating_new_keys(req: Request, activation_key: str, db: Session = Depends(db_session)):
    return activate_new_key(req, activation_key, db)

