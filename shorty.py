from fastapi import FastAPI
from routers.redirect import redirect_router
from routers.random_url import random_router
from routers.register import register_route
from routers.custom_url import custom_router
from routers.delete import delete_router
from database.models import Base
from database.database import engine
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter import req_limiter


shorty = FastAPI(title="ShortyAPI",
                 description="Url shortener for practice",
                 version="0.1",
                 )

shorty.state.limiter = req_limiter
shorty.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

shorty.include_router(redirect_router)
shorty.include_router(random_router)
shorty.include_router(register_route)
shorty.include_router(custom_router)
shorty.include_router(delete_router)

Base.metadata.create_all(engine)
