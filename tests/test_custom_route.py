from httpx import AsyncClient
from conf_test_db import shorty, override_db_session
from routers_functions.scope_all import expire_date
from database.models import DbShort
from tests.test_custom_route_fixtures import *


@pytest.mark.asyncio()
async def test_create_new_custom_without_api_key(base_url, no_key_request):
    """Test standard response for creating custom_short_url without Api-key"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        test_url = no_key_request.origin_url
        test_name = no_key_request.custom_name
        test_expire_days = no_key_request.expire_days
        response = await client.post("/custom/add",
                                     json={"origin_url": test_url,
                                           "custom_name": test_name,
                                           "expire_days": test_expire_days}
                                     )
        assert response.status_code == 200
        created_short = base_url + test_name
        exist = database.query(DbShort).filter_by(short_url=created_short).first()
        expire_target = expire_date(days=test_expire_days)
        assert exist
        assert exist.origin_url == test_url
        assert exist.api_key is None
        assert expire_target.day == exist.expire_date.day


@pytest.mark.asyncio
async def test_create_new_custom_with_api_key(base_url, with_key_entity, with_key_request):
    """Test standard response for creating custom_short_url with Api-key"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        database.add(with_key_entity)
        database.commit()
        test_api_key = with_key_entity.api_key
        key_exist = database.query(DbKeys).filter_by(api_key=test_api_key).first()
        assert key_exist.activated is True
        test_url = with_key_request.origin_url
        test_name = with_key_request.custom_name
        test_expire_days = with_key_request.expire_days
        response = await client.post("/custom/add",
                                     headers={"api-key": test_api_key},
                                     json={"origin_url": test_url,
                                           "custom_name": test_name,
                                           "expire_days": test_expire_days}
                                     )
        assert response.status_code == 200
        created_short = base_url + test_name
        exist = database.query(DbShort).filter_by(short_url=created_short).first()
        assert exist
        assert exist.api_key == test_api_key
        expire_target = expire_date(days=test_expire_days)
        assert expire_target.day == exist.expire_date.day


@pytest.mark.asyncio
async def test_create_new_custom_with_length_limits(base_url):
    """Test standard responses for length limits"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        max_length = 30
        test_url = "https://docs.python.org/3.11/"
        test_name = "".join(random.choices(string.ascii_letters, k=max_length + 1))
        empty_name = ""
        max_length_response = await client.post("/custom/add",
                                                json={"origin_url": test_url,
                                                      "custom_name": test_name}
                                                )
        assert max_length_response.status_code == 400
        created_short = base_url + test_name
        exist = database.query(DbShort).filter_by(short_url=created_short).first()
        assert exist is None
        empty_string_response = await client.post("/custom/add",
                                                  json={"origin_url": test_url,
                                                        "custom_name": empty_name}
                                                  )
        assert empty_string_response.status_code == 400
        created_short = base_url + empty_name
        exist = database.query(DbShort).filter_by(short_url=created_short).first()
        assert exist is None


@pytest.mark.asyncio
async def test_create_new_custom_expire_limit_without_api_key(base_url, no_key_request):
    """Test standard responses for expire limits without Api-key"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        test_url = no_key_request.origin_url
        test_name = "expire_limit_without_key_"
        max_expire = 10
        min_expire = 1
        test_values = [max_expire + 1, min_expire - 1, -100]
        for value in test_values:
            response = await client.post("custom/add",
                                         json={"origin_url": test_url,
                                               "custom_name": test_name,
                                               "expire_days": value}
                                         )
            assert response.status_code == 400
            created_short = base_url + test_name
            exist = database.query(DbShort).filter_by(short_url=created_short).first()
            assert exist is None


@pytest.mark.asyncio
async def test_create_new_custom_expire_limit_with_api_key(base_url, with_key_request, limits_entity_with_key):
    """Test standard responses for expire limits with Api-key"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        database.add(limits_entity_with_key)
        database.commit()
        test_url = with_key_request.origin_url
        test_name = "expire_limit_with_key_"
        max_expire = 30
        min_expire = 1
        test_api_key = limits_entity_with_key.api_key
        key_exist = database.query(DbKeys).filter_by(api_key=test_api_key).first()
        assert key_exist.activated is True
        test_values = [max_expire + 1, min_expire - 1, -100]
        for value in test_values:
            response = await client.post("custom/add",
                                         headers={"api-key": test_api_key},
                                         json={"origin_url": test_url,
                                               "custom_name": test_name,
                                               "expire_days": value}
                                         )
            assert response.status_code == 400
            created_short = base_url + test_name
            exist = database.query(DbShort).filter_by(short_url=created_short).first()
            assert exist is None
