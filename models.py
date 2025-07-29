from sqlalchemy import Column, Integer, String
from database import Base

# Users Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# Devices table
class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    device_name = Column(String, nullable=False)
    application_code = Column(String, nullable=False)
    secret_key = Column(String, nullable=False)
