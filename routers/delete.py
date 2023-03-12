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
                    )
async def clear_expired(admin_key: str = Header(),
                        db_model: str = Header("all"),
                        db: Session = Depends(db_session)
                        ):
    return delete_all_expired_in_table(admin_key=admin_key, db=db, db_model=db_model)
