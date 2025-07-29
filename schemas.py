# To define models for validating and parsing request data
from pydantic import BaseModel

# Schema for registering / creating a new user
class UserCreate(BaseModel):
    username: str
    password: str
    company_name: str
    address: str
    phone : str
    application_code: str
    secret_key: str


# Schema for User login authentication requests
class UserLogin(BaseModel):
    username: str
    password: str

# Schema for sending JWT / OAuth2 access token back to the client after login
class TokenResponse(BaseModel):
    access_token: str
    # bearer is the standard for OAuth2-style APIs
    token_type: str = "bearer"

# Schema for creating / registering a new device
class DeviceCreate(BaseModel):
    name: str
    application_code: str
    secret_key: str

# Schema for response model 
class DeviceOut(BaseModel):
    id: int
    name: str

    class Config:
        # 'orm_mode' has been renamed to 'from_attributes'
        from_attributes = True
