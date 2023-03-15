from database.database import Base
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class DbRandom(Base):
    __tablename__ = "random"
    short_url = Column(String(length=50), primary_key=True, nullable=False)
    origin_url = Column(String(length=200), nullable=False)
    expire_date = Column(DateTime, nullable=False)


class DbCustom(Base):
    __tablename__ = "custom"
    short_url = Column(String(length=200), primary_key=True, nullable=False)
    origin_url = Column(String(length=200), nullable=False)
    expire_date = Column(DateTime, nullable=False)

    api_key = Column(String, ForeignKey("api_keys.api_key"), nullable=True)
    key_user = relationship("DbKeys", back_populates="custom_urls")


class DbKeys(Base):
    __tablename__ = "api_keys"
    email = Column(String(length=80), primary_key=True, nullable=False)
    username = Column(String(length=80), nullable=False)
    api_key = Column(String(length=11), nullable=False)
    activation_link = Column(String(length=12), nullable=False)
    link_send = Column(Boolean, nullable=False)
    activated = Column(Boolean, nullable=False)
    expire_date = Column(DateTime, nullable=True)

    custom_urls = relationship("DbCustom", back_populates="key_user")
