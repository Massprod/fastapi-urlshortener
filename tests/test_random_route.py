import httpx
import pytest
from httpx import AsyncClient
from conf_test_db import shorty, override_db_session
from routers_functions.scope_all import expire_date
from database.models import DbRandom

max_length = 10
min_length = 4
expire_days_target = 7


@pytest.mark.asyncio
async def test_add_new_random():
    """Test standard response with correct data"""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        db = next(override_db_session())
        response_1 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": min_length}
                                       )
        assert response_1.status_code == 200
        created_short_1 = response_1.json()["short_url"]
        db_record_2 = db.query(DbRandom).filter_by(short_url=created_short_1).first()
        assert db_record_2
        target_expire_date = expire_date(days=expire_days_target)
        assert target_expire_date.day == db_record_2.expire_date.day
        response_2 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": max_length}
                                       )
        assert response_2.status_code == 200


@pytest.mark.asyncio
async def test_add_new_random_with_broken_url():
    """Test standard response with not working Url"""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        response = await client.post("/random/add",
                                     json={"origin_url": "https://www.reddit.com/testetes",
                                           "short_length": min_length}
                                     )
        assert response.status_code == 400
        timeout_response = await client.post("/random/add",
                                             json={"origin_url": "https://pikabu.ru/dasd",
                                                   "short_length": max_length}
                                             )
        assert timeout_response.status_code == 400


@pytest.mark.asyncio
async def test_add_new_random_with_wrong_length():
    """Test standard response with not supported length"""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        response_1 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": max_length + 1}
                                       )
        assert response_1.status_code == 400
        response_2 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": min_length - 1}
                                       )
        assert response_2.status_code == 400
        response_3 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": min_length * -1}
                                       )
        assert response_3.status_code == 400


@pytest.mark.asyncio
async def test_add_new_random_infinite_limit(mocker):
    """Test standard response with creating duplicated of short_url, and trying to insert in Db"""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        database = next(override_db_session())
        short_duplicate = "test_loop_out"
        mocker.patch("routers_functions.random_url_functions.create_rshort",
                     return_value=short_duplicate)
        response = await client.post("/random/add",
                                     json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                           "short_length": 5}
                                     )
        assert response.status_code == 200
        inserted_short = response.json()["short_url"]
        exist = database.query(DbRandom).filter_by(short_url=inserted_short).first()
        assert exist
        response_2 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": 5})
        assert response_2.status_code == 508
        assert pytest.raises(httpx.HTTPStatusError)
