# passlib for hashing and verifying the passwords
from passlib.context import CryptContext

from fastapi import HTTPException

# Session for databse session
from sqlalchemy.orm import Session

# Jose for token JWT token encoding decoding
from jose import JWTError, jwt

# From Folders import
from models import User
from database import SessionLocal

# To read and load environment files
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load up env variables
JWT_SECRET_KEY_128 = os.getenv("OPA_APP_CODE")  or "super-secret"

# JWT signing algorithm - HMAC SHA-256
JWT_SIGNING_ALGORITHM = "HS256"

# Password context for hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    # Create a db sesssion insance from SessionLocal()
    db = SessionLocal()
    try:
        # Returns the session for use in route handlers
        yield db
    finally:
        # Ensure its closed after use for preventing leaks
        db.close()

def hash_password(password: str):
    # Hash the plain password string
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    # Verify plain text password against a stored hash
    return pwd_context.verify(plain, hashed)


