from conf_test_db import shorty, override_db_session
from sqlalchemy.orm.session import Session
from database.database import db_session
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_random():
    async with AsyncClient(app=shorty, base_url="http://test") as ac:
        database = next(override_db_session())
        response = await ac.post("/random/add", json={
            "origin_url": "https://www.pythonanywhere.com/",
            "short_length": 3
        })
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_session():
    assert isinstance(next(db_session()), Session)
