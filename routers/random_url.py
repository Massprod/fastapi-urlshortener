from fastapi import APIRouter, Depends, Request
from schemas.schemas import RandomShort, RandomShortResponse
from database.database import db_session
from sqlalchemy.orm.session import Session
from routers_functions.random_url_functions import create_new_random

random_router = APIRouter(prefix="/random",
                          tags=["random"],
                          )


@random_router.post("/add",
                    name="Create new short",
                    response_model=RandomShortResponse,
                    description="Creating random Url with given length for provided Url",
                    response_description="Correct Json response with Url and Short version to redirect from",
                    )
async def add_new_random(req: Request,
                         data: RandomShort,
                         db: Session = Depends(db_session)
                         ):
    return create_new_random(req, data, db)
