from fastapi import APIRouter, Depends, Request
from schemas.schemas import RandomShort, RandomShortResponse
from database.database import db_session
from sqlalchemy.orm.session import Session
from routers_functions.random_url_functions import create_new_random
from limiter import req_limiter, random_limit


random_router = APIRouter(prefix="/random",
                          tags=["random"],)


@random_router.post("/add",
                    name="Create new short",
                    response_model=RandomShortResponse,
                    description="Creating random Url with given length for provided Url",
                    response_description="Correct Json response with Url and Short version to redirect from",
                    )
@req_limiter.limit(random_limit)
async def add_new_random(request: Request,
                         data: RandomShort,
                         db: Session = Depends(db_session)
                         ):
    return create_new_random(request, data, db)
