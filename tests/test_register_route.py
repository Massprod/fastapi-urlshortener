import pytest
from httpx import AsyncClient
from conf_test_db import shorty, override_db_session
from database.models import DbKeys
from routers_functions.scope_all import expire_date
from datetime import datetime, timedelta
from schemas.schemas import NewKey

correct_new_key = NewKey(email="test_send@gmail.com",
                         username="test_name")

wrong_new_key = NewKey(email="test wrong@supppose_wrong.com",
                       username="test_name_2")

test_expired_email = DbKeys(email="expired_email@gmail.com",
                            username="not_expired_username",
                            api_key="123456789",
                            activation_link="expired_email",
                            link_send=True,
                            activated=False,
                            expire_date=datetime.utcnow() - timedelta(days=1),
                            )
test_expired_username = DbKeys(email="not_expired@gmail.com",
                               username="expired_username",
                               api_key="987654321",
                               activation_link="expired_name",
                               link_send=True,
                               activated=False,
                               expire_date=datetime.utcnow() - timedelta(days=1),
                               )


@pytest.mark.asyncio
async def test_register_new_key():
    """Test standard response for creating new api-key"""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        database = next(override_db_session())
        test_email = correct_new_key.email
        test_username = correct_new_key.username
        response = await client.post("/register/new",
                                     json={"email": test_email,
                                           "username": test_username}
                                     )
        assert response.status_code == 200
        response_body = response.json()
        assert response_body["link_send"] is True
        record = database.query(DbKeys).filter_by(email=test_email).first()
        assert record.activation_link
        target_expire_date = expire_date(days=1)
        assert target_expire_date.day == record.expire_date.day


@pytest.mark.asyncio
async def test_register_new_key_with_empty_username():
    async with AsyncClient(app=shorty, base_url="https://test") as client:
        response = await client.post("/register/new",
                                     json={"email": "empty",
                                           "username": ""
                                           }
                                     )
        assert response.status_code == 400


# There's no verification for REAL_EMAIL in smtplib. This why we can
# send email anywhere and only after get email with receiver not found,
# but instantly raise error if domain is wrong. Only way to test this.
@pytest.mark.asyncio
async def test_register_new_key_with_wrong_domain():
    """Test standard response with wrong email domain"""
    async with AsyncClient(app=shorty, base_url="http://test") as client:
        test_email = wrong_new_key.email
        test_username = wrong_new_key.username
        response = await client.post("/register/new",
                                     json={"email": test_email,
                                           "username": test_username}
                                     )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_new_key_with_existing_credentials():
    """Test standard response for already existed email, username"""
    async with AsyncClient(app=shorty, base_url="https://test") as client:
        existed_email = correct_new_key.email
        existed_username = correct_new_key.username
        test_email = wrong_new_key.email
        test_username = wrong_new_key.username
        database = next(override_db_session())
        response_1 = await client.post("/register/new",
                                       json={"email": existed_email,
                                             "username": test_username}
                                       )
        assert response_1.status_code == 403
        assert database.query(DbKeys).filter_by(username=test_username).first() is None
        response_2 = await client.post("/register/new",
                                       json={"email": test_email,
                                             "username": existed_username}
                                       )
        assert response_2.status_code == 403
        assert database.query(DbKeys).filter_by(email=test_email).first() is None


@pytest.mark.asyncio
async def test_register_new_key_with_expired_email():
    """Test standard response for overriding already existed email BUT expired"""
    async with AsyncClient(app=shorty, base_url="https://test") as client:
        database = next(override_db_session())
        database.add(test_expired_email)
        database.commit()
        expired_email = test_expired_email.email
        expired_email_record = database.query(DbKeys).filter_by(email=expired_email).first()
        time_of_email_expiration = expired_email_record.expire_date
        response_exp_email = await client.post("/register/new",
                                               json={"email": expired_email,
                                                     "username": "not_already_used_name"}
                                               )
        database.refresh(expired_email_record)
        updated_email = expired_email_record.email
        updated_email_expire_time = expired_email_record.expire_date
        assert response_exp_email.status_code == 200
        assert updated_email == expired_email
        assert updated_email_expire_time > time_of_email_expiration


@pytest.mark.asyncio
async def test_register_new_key_with_expired_username():
    """Test standard response for overriding already existed username BUT expired"""
    async with AsyncClient(app=shorty, base_url="https://test") as client:
        database = next(override_db_session())
        database.add(test_expired_username)
        database.commit()
        expired_username = test_expired_username.username
        expired_username_record = database.query(DbKeys).filter_by(username=expired_username).first()
        expired_username = expired_username_record.username
        time_of_username_expiration = expired_username_record.expire_date
        response_exp_username = await client.post("/register/new",
                                                  json={"email": "not_already_used@gmail.com",
                                                        "username": expired_username}
                                                  )
        # changed Email, and it's primary key, so refresh won't work I need NEW object
        updated_username_record = database.query(DbKeys).filter_by(username=expired_username).first()
        updated_username = updated_username_record.username
        updated_username_expire_time = updated_username_record.expire_date
        assert response_exp_username.status_code == 200
        assert updated_username == expired_username
        assert updated_username_expire_time > time_of_username_expiration
