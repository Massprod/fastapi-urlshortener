from database.database import Base
from sqlalchemy import Column, Integer, String


class DbRandom(Base):
    __tablename__ = "random"
    rshort_url = Column(String(length=50), primary_key=True, nullable=False)
    origin_url = Column(String(length=200), nullable=False)


# class DbCustom(Base):
#     __tablename__ = "custom"
#     id = Column(Integer, primary_key=True, index=True)
#     origin_url = Column(String(length=200), nullable=False)
#     custom_url = Column(String(length=200), nullable=False)
