from fastapi import APIRouter, Request, Depends, Header, Path
from sqlalchemy.orm import Session
from database.database import db_session
from schemas.schemas import CustomShort, CustomShortResponse, ShowAllResponse, DeleteCustomResponse
from routers_functions.custom_url_functions import create_new_custom, show_all_email_customs, delete_by_api_key

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
                                                           "and expend Expire limit to 30 days"
                                               )
                         ):
    return create_new_custom(req, data, db, api_key)


@custom_router.get("/all",
                   name="Get all custom shorts",
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


@custom_router.delete("/delete/{custom_name}",
                      name="Delete custom short",
                      response_model=DeleteCustomResponse,
                      description="Deletes custom short by taking it's Name and Api-key which created it",
                      response_description="Correct Json response with deleted data and Time of the call",
                      )
async def delete_custom_url(req: Request,
                            custom_name: str = Path(description="Created custom name, used in the end of custom Url",
                                                    example="provision",
                                                    ),
                            api_key: str = Header(description="Api-key provided after registration"),
                            db: Session = Depends(db_session)):
    return delete_by_api_key(req, custom_name, api_key, db)
