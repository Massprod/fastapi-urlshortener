from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session
from database.database import db_session
from schemas.schemas import DeleteExpiredResponse
from routers_functions.delete_functions import delete_all_expired_in_table
from limiter import req_limiter, delete_limit


delete_router = APIRouter(prefix="/delete",
                          tags=["delete"],)


@delete_router.delete("/expired",
                      name="Delete all expired records from Db",
                      response_model=DeleteExpiredResponse,
                      description="Deletes all expired records from given Table in Db",
                      response_description="Correct Json response with cleared Table and call time",
                      )
@req_limiter.limit(delete_limit)
async def clear_expired(request: Request,  # required by limiter
                        admin_key: str = Header(description="Required access key"),
                        db_model: str = Header("all",
                                               description="Table name"),
                        db: Session = Depends(db_session)
                        ):
    return delete_all_expired_in_table(admin_key=admin_key, db=db, db_model=db_model)
