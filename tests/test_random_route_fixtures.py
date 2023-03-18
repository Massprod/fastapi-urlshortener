from schemas.schemas import RandomShort
import pytest


@pytest.fixture(scope="session")
def base_url():
    return "https://test/"


@pytest.fixture(scope="function")
def expired_short_request():
    return RandomShort(origin_url="https://coverage.readthedocs.io/en/7.1.0/")


@pytest.fixture(scope="function")
def expired_short_override_request():
    return RandomShort(origin_url="https://www.reddit.com/")
