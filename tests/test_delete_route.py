from httpx import AsyncClient
from conf_test_db import shorty, override_db_session
from tests.test_delete_route_fixtures import *
import os


@pytest.mark.asyncio
async def test_delete_route_with_all_tables(base_url,
                                            delete_all_keys_expired_entity,
                                            delete_all_short_expired_entity,
                                            ):
    """Test response for deleting expired records in ALL existing tables"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        database.add(delete_all_short_expired_entity)
        database.add(delete_all_short_expired_entity)
        database.commit()
        test_admin_key = os.getenv("ADMIN_KEY")
        test_tables = "all"
        test_api_key = delete_all_keys_expired_entity.api_key
        test_short_url = delete_all_short_expired_entity.short_url
        response = await client.delete("/delete/expired",
                                       headers={"admin-key": test_admin_key,
                                                "db-model": test_tables,
                                                }
                                       )
        assert response.status_code == 200
        key_still_exist = database.query(DbKeys).filter_by(api_key=test_api_key).first()
        assert not key_still_exist
        url_still_exist = database.query(DbShort).filter_by(short_url=test_short_url).first()
        assert not url_still_exist


@pytest.mark.asyncio
async def test_delete_route_with_one_table(base_url,
                                           delete_table_keys_expire_entity,
                                           delete_table_short_expire_entity,
                                           ):
    """Test responses for deleting expired records in ONE existing table"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        database = next(override_db_session())
        database.add(delete_table_short_expire_entity)
        database.add(delete_table_keys_expire_entity)
        database.commit()
        test_admin_key = os.getenv("ADMIN_KEY")
        test_tables = ["dbkeys", "dbshort"]
        test_short_url = delete_table_short_expire_entity.short_url
        test_api_key = delete_table_keys_expire_entity.api_key
        for table in test_tables:
            response = await client.delete("/delete/expired",
                                           headers={"admin-key": test_admin_key,
                                                    "db-model": table,
                                                    }
                                           )
            assert response.status_code == 200
        key_exist = database.query(DbKeys).filter_by(api_key=test_api_key).first()
        assert not key_exist
        url_exist = database.query(DbShort).filter_by(short_url=test_short_url).first()
        assert not url_exist


@pytest.mark.asyncio
async def test_delete_route_with_wrong_table(base_url):
    """Test response for deleting expired records with WRONG table name"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        test_admin_key = os.getenv("ADMIN_KEY")
        test_table_name = "randomName"
        response = await client.delete("/delete/expired",
                                       headers={"admin-key": test_admin_key,
                                                "db-model": test_table_name,
                                                }
                                       )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_route_with_wrong_access_key(base_url):
    """Test response for using wrong access key"""
    async with AsyncClient(app=shorty, base_url=base_url) as client:
        test_admin_key = "anyOtherKeyTyped"
        response = await client.delete("/delete/expired",
                                       headers={"admin-key": test_admin_key},
                                       )
        assert response.status_code == 403
