import os
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import DbKeys, DbCustom, DbRandom
from schemas.schemas import DeleteExpiredResponse
from routers_functions.scope_all import del_expired


def delete_all_expired_in_table(admin_key: str, db: Session, db_model: str = "all", ):
    """Deletes expired records from given table or all tables of provided DB"""
    call_time = datetime.utcnow()
    chosen_table = db_model.lower().replace(" ", "")
    if admin_key == os.getenv("admin_key"):
        tables = [DbKeys, DbCustom, DbRandom]
        if chosen_table == "all":
            for _ in tables:
                del_expired(db_model=_, db=db, delete_all=True)
            return DeleteExpiredResponse(table="all", call_time=call_time)
        chosen_table = [_ for _ in tables if _.__name__.lower() == chosen_table]
        chosen_table = chosen_table[0]  # bad solution, but better looking than for_loop and might be faster
        if chosen_table not in tables:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Table doesn't exist")
        elif chosen_table:
            del_expired(db_model=chosen_table, db=db, delete_all=True)
            return DeleteExpiredResponse(table=chosen_table.__name__, call_time=call_time)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Wrong Admin-key")
