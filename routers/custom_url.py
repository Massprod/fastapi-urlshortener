from fastapi import APIRouter, Request, Depends, Header
from sqlalchemy.orm import Session
from database.database import db_session
from schemas.schemas import CustomShort, CustomShortResponse, ShowAllResponse
from routers_functions.custom_url_functions import create_new_custom, show_all_email_customs

custom_router = APIRouter(prefix="/custom",
                          tags=["custom"])


@custom_router.post("/add",
                    name="Create new custom short",
                    response_model=CustomShortResponse,
                    description="Creating custom named version of provided Url",
                    response_description="Correct Json response with Url and custom version of it to redirect from",
                    )
async def add_new_custom(req: Request,
                         data: CustomShort,
                         db: Session = Depends(db_session),
                         api_key: str = Header(None,
                                               description="Optional. "
                                                           "Use to associate Api-key with custom Urls "
                                                           "and expend Expire limit to 30 days")
                         ):
    return create_new_custom(req, data, db, api_key)


@custom_router.get("/show/all",
                   name="Show all records",
                   response_model=ShowAllResponse,
                   description="Return JSON with all created custom short Urls by given Identifier",
                   response_description="Correct Json response with all data for this Identifier",
                   )
async def show_all_customs(identifier: str = Header(example="piankovpe@gmail.com",
                                                    description="One of Unique Identifiers: Username, Email, Api-key"
                                                    ),
                           db: Session = Depends(db_session),
                           ):
    return show_all_email_customs(identifier, db)
