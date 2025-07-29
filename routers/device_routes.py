# For creating router, thorwing exception, dependency injection, extract http headers
from fastapi import APIRouter, Depends, HTTPException, Header

# For creating session
from sqlalchemy.orm import Session

# Custom modules import
from auth import decode_token, get_db
from models import Device, User
from schemas import DeviceCreate, DeviceOut

# For defining response model
from typing import List

# Router object to handle routing
router = APIRouter()

# Dependency to get authenticated user from request
def get_current_user(token: str = Header(...), db: Session = Depends(get_db)) -> User:
    # Token reads "token" HTTP header from incoming request 
    # Session injects a db session

    # Decode and verify the token
    user_data = decode_token(token)

    # Query db and check for the user name
    user = db.query(User).filter(User.username == user_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return ORM object if found
    return user

# Endpoint for adding a new device
@router.post("/add-device")
def add_device(
    device: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # First device is validated with Devicecreate
    # Dependency inject the current user to get the authenticated user
    # db injects a db session

    # Create a new instance of ORM object
    new_device = Device(
        user_id=current_user.id,
        device_name=device.name,
        application_code=device.application_code,
        secret_key=device.secret_key
    )

    # Add to db and commit the transaction
    db.add(new_device)
    db.commit()

    # Refresh the instance to populat it with any new data
    db.refresh(new_device)

    # Return a JSON confirming
    return {"message": "Device added successfully", "device_id": new_device.id}

# Get endpoint to get a list of all devices based on DeviceOut format
@router.get("/devices", response_model=List[DeviceOut])
def list_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Depedency inject current authenticated user and db session

    # Query and retrieve all devices
    devices = db.query(Device).filter(Device.user_id == current_user.id).all()

    # Construct a list of Deviceout Pydantic objects and return as json
    return [
        DeviceOut(id=d.id, name=d.device_name, application_code=d.application_code)
        for d in devices
    ]
