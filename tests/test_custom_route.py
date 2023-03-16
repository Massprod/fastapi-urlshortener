import pytest
from httpx import AsyncClient
from conf_test_db import shorty, override_db_session
from routers_functions.scope_all import expire_date
from schemas.schemas import CustomShort
from database.models import DbCustom, DbKeys

base_url = "http://test/"

test_no_key = CustomShort(origin_url="https://github.com/Massprod/UdemyFastAPI",
                          custom_name="nokeyused",
                          expire_days=5,
                          )
test_with_key = CustomShort(origin_url="https://github.com/Massprod/UdemyFastAPI",
                            custom_name="keyused",
                            expire_days=20,
                            )

max_custom_length = 30
min_custom_length = 1

max_expire_time_no_key = 10
max_expire_time_with_key = 30

min_expire_time_no_key = 1
min_expire_time_with_key = 1


@pytest.mark.asyncio
async def test_create_new_custom_without_api_key():
    """Test standard response for creating custom_short_url without Api-key"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        test_url = test_no_key.origin_url
        test_name = test_no_key.custom_name
        test_expire_days = test_no_key.expire_days
        response = await client.post("/custom/add",
                                     json={"origin_url": test_url,
                                           "custom_name": test_name,
                                           "expire_days": test_expire_days}
                                     )
        assert response.status_code == 200
        created_short = base_url + test_name
        exist = database.query(DbCustom).filter_by(short_url=created_short).first()
        expire_target = expire_date(days=test_expire_days)
        assert exist
        assert exist.origin_url == test_url
        assert exist.api_key is None
        assert expire_target.day == exist.expire_date.day


# @pytest.mark.asyncio
# async def test_create_new_custom_with_api_key():
#     """Test standard response for creating custom_short_url with Api-key"""
#     async with AsyncClient(app=shorty, base_url=base_url) as client:

