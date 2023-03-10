from fastapi import APIRouter, Request, Depends, Header
from sqlalchemy.orm import Session
from database.database import db_session
from schemas.schemas import CustomShort, CustomShortResponse
from routers_functions.custom_url_functions import create_new_custom


custom_router = APIRouter(prefix="/custom",
                          tags=["custom"]
                          )


@custom_router.post("/add",
                    name="Create new custom short",
                    response_model=CustomShortResponse,
                    description="Creating custom named short URL for provided URL",
                    response_description="Return JSON with URL and CUSTOM version of it to redirect from",
                    )
def add_new_custom(req: Request, data: CustomShort, db: Session = Depends(db_session), api_key: str = Header(None)):
    return create_new_custom(req, data, db, api_key)
