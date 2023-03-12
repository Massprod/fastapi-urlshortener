from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from database.database import db_session
from schemas.schemas import DeleteExpiredResponse
from routers_functions.delete_functions import delete_all_expired_in_table


delete_router = APIRouter(prefix="/delete",
                          tags=["delete"])


@delete_router.post("/expired",
                    name="Delete all expired records from Db",
                    response_model=DeleteExpiredResponse,
                    description="Deletes all expired records from given Table in Db",
                    response_description="Correct Json response with cleared Table and call time",
                    )
async def clear_expired(admin_key: str = Header(description="Required access key"),
                        db_model: str = Header("all",
                                               description="Table name"),
                        db: Session = Depends(db_session)
                        ):
    return delete_all_expired_in_table(admin_key=admin_key, db=db, db_model=db_model)
