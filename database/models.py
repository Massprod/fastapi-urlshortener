from database.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean


class DbRandom(Base):
    __tablename__ = "random"
    rshort_url = Column(String(length=50), primary_key=True, nullable=False)
    origin_url = Column(String(length=200), nullable=False)
    expire_date = Column(DateTime, nullable=False)


class DbCustom(Base):
    __tablename__ = "custom"
    id = Column(Integer, primary_key=True, index=True)
    origin_url = Column(String(length=200), nullable=False)
    custom_url = Column(String(length=200), nullable=False)
    expire_date = Column(DateTime, nullable=False)


class DbKeys(Base):
    __tablename__ = "api_keys"
    api_key = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    activation_link = Column(String, nullable=False)
    link_send = Column(Boolean, nullable=False)
    activated = Column(Boolean, nullable=False)
