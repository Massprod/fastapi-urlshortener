import pytest
from schemas.schemas import CustomShort
from database.models import DbKeys, DbShort

# pytest see these fixtures, but I can't use them anywhere before explicitly Import them.
# How I understand: they should be Session wide once created, and used without imports.
# Change it if I find why/how.


@pytest.fixture(scope="session")
def base_url():
    return "http://test/"


@pytest.fixture(scope="function")
def no_key_request():
    return CustomShort(origin_url="https://github.com/Massprod/FastAPI_UrlShort",
                       custom_name="nokeyused",
                       expire_days=5,
                       )


@pytest.fixture(scope="function")
def with_key_entity():
    return DbKeys(email="test_custom_with_key@gmail.com",
                  username="test_custom_with_key",
                  api_key="test_with",
                  activation_link="activated_with_key",
                  link_send=True,
                  activated=True,
                  expire_date=None,
                  )


@pytest.fixture(scope="function")
def with_key_request():
    return CustomShort(origin_url="https://github.com/Massprod/UdemyFastAPI",
                       custom_name="keyused",
                       expire_days=20,
                       )


@pytest.fixture(scope="function")
def limits_entity_with_key():
    return DbKeys(email="test_expire_with_key@gmail.com",
                  username="test_expire_with_key",
                  api_key="test_expire",
                  activation_link="expire_key",
                  link_send=True,
                  activated=True,
                  expire_date=None,
                  )


@pytest.fixture(scope="function")
def with_broken_url():
    return CustomShort(origin_url="https://www.reddit.com/sdsddsdsdf",
                       custom_name="broken_url",
                       expire_days=5,
                       )


@pytest.fixture(scope="function")
def duplicate_request():
    return CustomShort(origin_url="https://github.com/Massprod",
                       custom_name="duplicate_custom",
                       expire_days=5,
                       )
