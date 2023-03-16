from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database.models import DbShort
from routers_functions.scope_all import del_expired


def redirect(req: Request, short_key: str, db: Session):
    short_url = req.base_url.url + short_key.replace(" ", "")  # next time create function to clear spaces, 3+ occurs
    tables = [DbShort]
    for _ in tables:
        del_expired(db_model=_, db=db, del_one_short=short_url)
        if exist := db.query(_).filter_by(short_url=short_url).first():
            return RedirectResponse(url=exist.origin_url,
                                    status_code=status.HTTP_302_FOUND)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Searched Url expired or never existed. Create a new one.")
