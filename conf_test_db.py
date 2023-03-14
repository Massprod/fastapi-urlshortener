from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, db_session
from shorty import shorty


SQL_URL = "sqlite:///tests/test_database.db"

engine = create_engine(SQL_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


shorty.dependency_overrides[db_session] = override_db_session
