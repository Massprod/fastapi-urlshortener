import httpx
from httpx import AsyncClient
from conf_test_db import shorty, override_db_session
from routers_functions.scope_all import expire_date, check_records_count
from database.models import DbShort
from math import factorial
from datetime import datetime, timedelta
from tests.test_random_route_fixtures import *

max_length = 10
min_length = 1
expire_days_target = 7


@pytest.mark.asyncio
async def test_add_new_random():
    """Test standard response with correct data"""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        db = next(override_db_session())
        response_1 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": min_length + 1}
                                       )
        assert response_1.status_code == 200
        created_short_1 = response_1.json()["short_url"]
        db_record_2 = db.query(DbShort).filter_by(short_url=created_short_1).first()
        assert db_record_2
        target_expire_date = expire_date(days=expire_days_target)
        assert target_expire_date.day == db_record_2.expire_date.day
        response_2 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": max_length - 1}
                                       )
        assert response_2.status_code == 200


@pytest.mark.asyncio
async def test_add_new_random_with_expired_short(base_url,
                                                 mocker,
                                                 expired_short_request,
                                                 expired_short_override_request,
                                                 ):
    """Test standard response with overriding expired duplicate"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        test_name = "duplicate_expire"
        test_expire = datetime.utcnow() - timedelta(days=1)
        test_url = expired_short_override_request.origin_url
        test_override_url = expired_short_request.origin_url
        mocker.patch("routers_functions.random_url_functions.create_rshort",
                     return_value=test_name)
        mocker.patch("routers_functions.random_url_functions.expire_date",
                     return_value=test_expire)
        new_record = await client.post("/random/add",
                                       json={"origin_url": test_override_url},
                                       )
        assert new_record.status_code == 200
        created_short = base_url + test_name
        new_record_exist = database.query(DbShort).filter_by(short_url=created_short).first()
        assert new_record_exist
        assert new_record_exist.origin_url == test_override_url
        assert new_record_exist.expire_date == test_expire
        override_record = await client.post("/random/add",
                                            json={"origin_url": test_url},
                                            )
        assert override_record.status_code == 200
        override_exist = database.query(DbShort).filter_by(short_url=created_short).first()
        database.refresh(override_exist)
        assert override_exist
        assert override_exist.origin_url == test_url
        assert new_record_exist.expire_date == test_expire


@pytest.mark.asyncio
async def test_add_new_random_with_broken_url():
    """Test standard response with not working Url"""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        response = await client.post("/random/add",
                                     json={"origin_url": "https://www.reddit.com/testetes",
                                           "short_length": min_length + 2}
                                     )
        assert response.status_code == 400
        timeout_response = await client.post("/random/add",
                                             json={"origin_url": "https://pikabu.ru/dasd",
                                                   "short_length": max_length - 2}
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
async def test_add_new_random_infinite_loop_break(mocker):
    """Test standard behaviour with infinitely creating same random_short
    and running out of all their combinations with given Length.
    Breaking infinite loop of creating short_urls."""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        database = next(override_db_session())
        test_length = 10
        test_short = "test2552"
        mocker.patch("routers_functions.random_url_functions.create_rshort",
                     return_value=test_short)
        mocker.patch("routers_functions.random_url_functions.check_records_count",
                     return_value=factorial(62) / factorial(62 - test_length))
        response_1 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": test_length}
                                       )
        assert response_1.status_code == 200
        created_short = "http://test/" + test_short
        exist = database.query(DbShort).filter_by(short_url=created_short).first()
        assert exist
        response_2 = await client.post("/random/add",
                                       json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                             "short_length": test_length}
                                       )
        assert response_2.status_code == 508
        assert pytest.raises(httpx.HTTPStatusError)
        assert database.query(DbShort).filter_by(short_url=created_short).count() == 1


@pytest.mark.asyncio
async def test_add_new_random_records_count():
    """Test correct function return with selected random_short length"""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        database = next(override_db_session())
        test_length = 1
        test_quantity = 5
        for _ in range(test_quantity):
            response = await client.post("/random/add",
                                         json={"origin_url": "https://github.com/Massprod/FastAPI_UrlShort",
                                               "short_length": test_length}
                                         )
            assert response.status_code == 200
            created_short = response.json()["short_url"]
            exist = database.query(DbShort).filter_by(short_url=created_short).first()
            assert exist
        exist_length_records = check_records_count(db=database, db_model=DbShort, length=test_length)
        assert exist_length_records == test_quantity
