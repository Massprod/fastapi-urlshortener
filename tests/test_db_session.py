from sqlalchemy import inspect
from sqlalchemy.orm.session import Session
from database.database import db_session, engine
from database.models import DbRandom, DbKeys, DbCustom
import pytest


@pytest.mark.asyncio
async def test_get_db_session():
    assert isinstance(next(db_session()), Session)


@pytest.mark.asyncio
async def test_created_tables():
    created_tables = inspect(engine).get_table_names()
    target_tables = [DbKeys.__tablename__, DbCustom.__tablename__, DbRandom.__tablename__]
    assert target_tables == created_tables
