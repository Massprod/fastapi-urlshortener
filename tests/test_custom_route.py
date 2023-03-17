import os

from httpx import AsyncClient
from conf_test_db import shorty, override_db_session
from routers_functions.scope_all import expire_date
from database.models import DbShort
from tests.test_custom_route_fixtures import *
import random
import string


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
                                           "expire_days": test_expire_days,
                                           }
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
                                           "expire_days": test_expire_days,
                                           }
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
                                                      "custom_name": test_name,
                                                      }
                                                )
        assert max_length_response.status_code == 400
        created_short = base_url + test_name
        exist = database.query(DbShort).filter_by(short_url=created_short).first()
        assert not exist
        empty_string_response = await client.post("/custom/add",
                                                  json={"origin_url": test_url,
                                                        "custom_name": empty_name,
                                                        }
                                                  )
        assert empty_string_response.status_code == 400
        created_short = base_url + empty_name
        exist = database.query(DbShort).filter_by(short_url=created_short).first()
        assert not exist


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
                                               "expire_days": value,
                                               }
                                         )
            assert response.status_code == 400
            created_short = base_url + test_name
            exist = database.query(DbShort).filter_by(short_url=created_short).first()
            assert not exist


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
                                               "expire_days": value,
                                               }
                                         )
            assert response.status_code == 400
            created_short = base_url + test_name
            exist = database.query(DbShort).filter_by(short_url=created_short).first()
            assert not exist


@pytest.mark.asyncio
async def test_create_new_custom_with_broken_url(base_url, with_broken_url):
    """Test standard response for broken Url"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        test_url = with_broken_url.origin_url
        test_name = with_broken_url.custom_name
        test_expire_days = with_broken_url.expire_days
        response = await client.post("/custom/add",
                                     json={"origin_url": test_url,
                                           "custom_name": test_name,
                                           "expire_days": test_expire_days,
                                           }
                                     )
        assert response.status_code == 400
        exist = database.query(DbShort).filter_by(origin_url=test_url).first()
        assert not exist


@pytest.mark.asyncio
async def test_create_new_custom_with_duplicated_custom_name(base_url, duplicate_request):
    """Test standard response for duplicated custom_name"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        test_url = duplicate_request.origin_url
        test_name = duplicate_request.custom_name
        test_expire_days = duplicate_request.expire_days
        response = await client.post("/custom/add",
                                     json={"origin_url": test_url,
                                           "custom_name": test_name,
                                           "expire_days": test_expire_days,
                                           }
                                     )
        assert response.status_code == 200
        duplicate_response = await client.post("/custom/add",
                                               json={"origin_url": test_url,
                                                     "custom_name": test_name,
                                                     "expire_days": test_expire_days,
                                                     }
                                               )
        assert duplicate_response.status_code == 403
        created_short = base_url + test_name
        exist = database.query(DbShort).filter_by(short_url=created_short).first()
        assert exist


@pytest.mark.asyncio
async def test_show_all_custom_with_activated_api_key(base_url,
                                                      show_all_activated_reqs,
                                                      show_all_activated_entity,
                                                      ):
    """Test standard response for GET request with activated Api-key"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        database.add(show_all_activated_entity)
        database.commit()
        test_api_key = show_all_activated_entity.api_key
        key_exist = database.query(DbKeys).filter_by(api_key=test_api_key).first()
        assert key_exist
        assert key_exist.activated is True
        test_requests = show_all_activated_reqs
        for request in test_requests:
            response = await client.post("/custom/add",
                                         headers={"api-key": test_api_key},
                                         json={"origin_url": request.origin_url,
                                               "custom_name": request.custom_name,
                                               }
                                         )
            assert response.status_code == 200
            created_short = base_url + request.custom_name
            exist = database.query(DbShort).filter_by(short_url=created_short).first()
            assert exist
            assert exist.api_key == test_api_key
        test_email = show_all_activated_entity.email
        test_username = show_all_activated_entity.username
        test_identifiers = [test_api_key, test_username, test_email]
        for identifier in test_identifiers:
            response = await client.get("/custom/all",
                                        headers={"identifier": identifier},
                                        )
            assert response.status_code == 200
            response_data = response.json()
            associated_urls = response_data["custom_urls"]
            assert len(associated_urls) == 3
            assert response_data["email"] == test_email


@pytest.mark.asyncio
async def test_show_all_custom_with_not_activated_api_key(base_url,
                                                          show_all_not_activated_reqs,
                                                          show_all_not_activated_entity,
                                                          ):
    """Test standard response for GET request with Not activated Api-key"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        database.add(show_all_not_activated_entity)
        database.commit()
        test_api_key = show_all_not_activated_entity.api_key
        key_exist = database.query(DbKeys).filter_by(api_key=test_api_key).first()
        assert key_exist
        assert key_exist.activated is False
        test_requests = show_all_not_activated_reqs
        for request in test_requests:
            response = await client.post("/custom/add",
                                         headers={"api-key": test_api_key},
                                         json={"origin_url": request.origin_url,
                                               "custom_name": request.custom_name,
                                               }
                                         )
            assert response.status_code == 200
            created_short = base_url + request.custom_name
            exist = database.query(DbShort).filter_by(short_url=created_short).first()
            assert exist
            assert exist.api_key == test_api_key
        test_email = show_all_not_activated_entity.email
        test_username = show_all_not_activated_entity.username
        test_identifiers = [test_email, test_api_key, test_username]
        for identifier in test_identifiers:
            response = await client.get("/custom/all",
                                        headers={"identifier": identifier},
                                        )
            assert response.status_code == 403


@pytest.mark.asyncio
async def test_show_all_custom_with_cascade_delete_expired_api_key(base_url,
                                                                   show_all_cascade_delete_entity,
                                                                   show_all_cascade_delete_reqs,
                                                                   ):
    """Test standard response for deleting children records with expired BUT already used Api-key.
    We allow using Api-key without activation, and delete all records and Key after expiration time."""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        database.add(show_all_cascade_delete_entity)
        database.commit()
        test_api_key = show_all_cascade_delete_entity.api_key
        key_exist = database.query(DbKeys).filter_by(api_key=test_api_key).first()
        admin_key = os.getenv("admin_key")
        assert key_exist
        assert key_exist.activated is False
        created_shorts = []
        test_requests = show_all_cascade_delete_reqs
        for request in test_requests:
            response = await client.post("/custom/add",
                                         headers={"api-key": test_api_key},
                                         json={"origin_url": request.origin_url,
                                               "custom_name": request.custom_name,
                                               }
                                         )
            assert response.status_code == 200
            created_short = base_url + request.custom_name
            created_shorts.append(created_short)
            exist = database.query(DbShort).filter_by(short_url=created_short).first()
            assert exist
            assert exist.api_key == test_api_key
        test_email = show_all_cascade_delete_entity.email
        test_username = show_all_cascade_delete_entity.username
        test_identifiers = [test_email, test_api_key, test_username]
        for identifier in test_identifiers:
            response = await client.get("/custom/all",
                                        headers={"identifier": identifier},
                                        )
            assert response.status_code == 403
        cascade_delete_response = await client.delete("/delete/expired",
                                                      headers={"admin-key": admin_key,
                                                               "db-model": "dbkeys",
                                                               }
                                                      )
        assert cascade_delete_response.status_code == 200
        for short in created_shorts:
            short_still_exist = database.query(DbShort).filter_by(short_url=short).first()
            assert short_still_exist is None
        key_still_exist = database.query(DbKeys).filter_by(api_key=test_api_key).first()
        assert key_still_exist is None
