import pytest
from database.models import DbKeys, DbShort
from datetime import datetime, timedelta


def set_expired(days: int):
    return datetime.utcnow() - timedelta(days=days)


@pytest.fixture(scope="session")
def base_url():
    return "https://test/"


@pytest.fixture(scope="function")
def delete_all_keys_expired_entity():
    return DbKeys(email="expiredInThisTable@gmail.com",
                  username="expiredInThisTable",
                  api_key="expTabl",
                  activation_link="expTabl",
                  link_send=True,
                  activated=False,
                  expire_date=set_expired(1),
                  )


@pytest.fixture(scope="function")
def delete_all_short_expired_entity():
    return DbShort(short_url="https://test/expired_on_birth",
                   origin_url="https://expired/already",
                   expire_date=set_expired(1),
                   )


@pytest.fixture(scope="function")
def delete_table_keys_expire_entity():
    return DbKeys(email="expiredOnBirth@gmail.com",
                  username="expireWhenIsee",
                  api_key="expTable",
                  activation_link="expTable",
                  link_send=True,
                  activated=False,
                  expire_date=set_expired(1),
                  )


@pytest.fixture(scope="function")
def delete_table_short_expire_entity():
    return DbShort(short_url="https://test/expired_table_delete",
                   origin_url="https://expire/alr",
                   expire_date=set_expired(1),
                   )
