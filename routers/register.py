from fastapi import APIRouter, Request, Depends, Path
from sqlalchemy.orm.session import Session
from schemas.schemas import NewKey, NewKeyResponse, ActivateResponse
from database.database import db_session
from routers_functions.register_functions import add_new_key, activate_new_key

register_route = APIRouter(prefix="/register",
                           tags=["register"],
                           )


@register_route.post(path="/new",
                     name="register new api-key",
                     response_model=NewKeyResponse,
                     description="Creating new API-KEY and sending to provided Email."
                                 "Not Active and expire in 1 day if not activated.",
                     response_description="Return JSON with registration data and sending "
                                          "activation link to provided Email",
                     )
def register_new_key(req: Request,
                     data: NewKey,
                     db: Session = Depends(db_session)
                     ):
    return add_new_key(req, data, db)


@register_route.get(path="/activate/{activation_key}",
                    name="activate registered api-key",
                    response_model=ActivateResponse,
                    description="Change activation status for registered API-KEY via provided "
                                "activation link",
                    response_description="Return JSON with data about activated API-KEY",
                    )
def activating_new_keys(req: Request,
                        activation_key: str = Path(description="Generated key from sent to Email Activation link"),
                        db: Session = Depends(db_session)
                        ):
    return activate_new_key(req, activation_key, db)
