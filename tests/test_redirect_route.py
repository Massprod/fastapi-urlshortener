from httpx import AsyncClient
from conf_test_db import shorty, override_db_session
from tests.test_redirect_route_fixtures import *
from database.models import DbShort


@pytest.mark.asyncio
async def test_redirect_route_correct(base_url,
                                      create_new_request
                                      ):
    """Test standard response for redirecting with correct Url"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        test_url = create_new_request.origin_url
        response = await client.post("/random/add",
                                     json={"origin_url": test_url},
                                     )
        assert response.status_code == 200
        created_short = response.json()["short_url"]
        exist = database.query(DbShort).filter_by(short_url=created_short).first()
        assert exist
        assert exist.origin_url == test_url
        redirect = await client.get(created_short)
        assert redirect.status_code == 302
        redirected = redirect.headers["location"]
        assert redirected == test_url


@pytest.mark.asyncio
async def test_redirect_route_with_wrong_url(base_url,
                                             not_existing_url,
                                             ):
    """Test standard response for redirecting with wrong Url"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        test_url = not_existing_url
        response = await client.get(test_url)
        assert response.status_code == 404
        exist = database.query(DbShort).filter_by(short_url=test_url).first()
        assert exist is None


@pytest.mark.asyncio
async def test_redirect_route_with_expired_url(base_url,
                                               redirect_expired_entity,
                                               ):
    """Test standard response for redirecting from expired Url"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        database.add(redirect_expired_entity)
        database.commit()
        test_url = redirect_expired_entity.short_url
        exist = database.query(DbShort).filter_by(short_url=test_url).first()
        assert exist
        response = await client.get(test_url)
        assert response.status_code == 404
        still_exist = database.query(DbShort).filter_by(short_url=test_url).first()
        assert not still_exist
