import pytest
from schemas.schemas import RandomShort
from database.models import DbShort
from datetime import datetime, timedelta


@pytest.fixture(scope="session")
def base_url():
    return "https://test/"


@pytest.fixture(scope="function")
def create_new_request():
    return RandomShort(origin_url="https://www.python.org/",
                       length=6,
                       )


@pytest.fixture(scope="function")
def not_existing_url():
    return "https://test/not_here_yet"


@pytest.fixture(scope="function")
def redirect_expired_entity():
    return DbShort(short_url="https://test/expired_already_here",
                   origin_url="https://www.python.org/",
                   expire_date=datetime.utcnow() - timedelta(days=1)
                   )

