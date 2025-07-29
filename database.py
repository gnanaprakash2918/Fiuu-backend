# To create the engine which is the starting point
from sqlalchemy import create_engine

# Session maker factory for creating session objects
# Declarative base returns a base class you use to dfine ORM class
from sqlalchemy.orm import sessionmaker, declarative_base

# Using SQLite
DATABASE_URL = "sqlite:///./fiuu_app.db"

# Allow any thread other than the one which created it to access
engine = create_engine(DATABASE_URL, connect_args = {"check_same_thread": False})

# No auto-commit until explicitly commited and Bind engine making sessions to use this engine to connect to db
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()
