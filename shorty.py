from fastapi import FastAPI
from routers.random import random_router
from database.models import Base
from database.database import engine


shorty = FastAPI()

shorty.include_router(random_router)

Base.metadata.create_all(engine)
