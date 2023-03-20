import os
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import DbKeys, DbShort
from schemas.schemas import DeleteExpiredResponse
from routers_functions.scope_all import del_expired


def delete_all_expired_in_table(admin_key: str, db: Session, db_model: str = "all", ):
    """Deletes expired records from given table or all tables of provided DB"""
    call_time = datetime.utcnow()
    chosen_model = db_model.lower().replace(" ", "")
    if admin_key == os.getenv("ADMIN_KEY"):
        models = [DbKeys, DbShort]
        if chosen_model == "all":
            for _ in models:
                del_expired(db_model=_, db=db, delete_all=True)
            return DeleteExpiredResponse(table="all", call_time=call_time)
        try:
            chosen_model = [_ for _ in models if _.__name__.lower() == chosen_model][0]
        except IndexError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Table with name: {chosen_model} doesn't exist")
        if chosen_model:
            del_expired(db_model=chosen_model, db=db, delete_all=True)
            return DeleteExpiredResponse(table=chosen_model.__name__, call_time=call_time)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Wrong Admin-key")
