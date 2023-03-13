from fastapi import APIRouter, Depends, Path, Request, status
from fastapi.responses import RedirectResponse
from database.database import db_session
from sqlalchemy.orm import Session
from routers_functions.redirect_functions import redirect

redirect_router = APIRouter(tags=["redirect"])


@redirect_router.get("/{short_key}",
                     name="redirecting page",
                     description="Redirecting to stored Url from given short version of it",
                     response_class=RedirectResponse,
                     status_code=status.HTTP_302_FOUND,
                     response_description="Correct response redirecting to stored origin Url",
                     )
async def redirect_page(req: Request,
                        short_key: str = Path(description="Custom or random key created for short version Url",
                                              example="provision"),
                        db: Session = Depends(db_session)
                        ):
    return redirect(req, short_key, db)
