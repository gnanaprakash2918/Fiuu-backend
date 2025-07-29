# For creating router, thorwing exception and dependency injection
from fastapi import APIRouter, Depends, HTTPException

# For creating session
from sqlalchemy.orm import Session

# Import our custom modules
from auth import get_db, hash_password, authenticate_user, create_token
from schemas import UserCreate, UserLogin
from models import User

# Router object to handle routing
router = APIRouter()

# Post endpoint for registering a user
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Parse Usercreate schema and inject db session

    # Before creating a new user, query db to check if username already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create a new ORM model with provided data and hash the password
    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password),
        company_name=user.company_name,
        address=user.address,
        phone=user.phone
    )

    # add new user instance to db session, commit and refresh it
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return success json on response
    return {"message": f"User {user.username} registered successfully"}

# Endpoint for logging in
@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # Authenticate the user first
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create A JWT token for authenticated users
    # this token will be used for subsequent requests
    token = create_token({"sub": user.username})

    # return the json with token and type
    return {"access_token": token, "token_type": "bearer"}
