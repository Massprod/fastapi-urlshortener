from fastapi import FastAPI
from routers.random_url import random_router
from routers.custom_url import custom_router
from routers.register import register_route
from database.models import Base
from database.database import engine

shorty = FastAPI()

shorty.include_router(random_router)
shorty.include_router(custom_router)
shorty.include_router(register_route)

Base.metadata.create_all(engine)
