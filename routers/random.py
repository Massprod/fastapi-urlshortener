from fastapi import APIRouter, Depends, Request
from schemas.schemas import RandomShort
from database.database import db_session
from sqlalchemy.orm.session import Session
from database.db_random import create_new_random


random_router = APIRouter(
    prefix="/random",
    tags=["random"],
)


@random_router.post("/add")
def add_new_random(req: Request, data: RandomShort, db: Session = Depends(db_session)):
    return create_new_random(req, data, db)
