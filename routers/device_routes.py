from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from auth import decode_token, get_db
from models import Device, User
from schemas import DeviceCreate, DeviceOut
from typing import List

router = APIRouter()

def get_current_user(token: str = Header(...), db: Session = Depends(get_db)) -> User:
    user_data = decode_token(token)
    user = db.query(User).filter(User.username == user_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/add-device")
def add_device(
    device: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_device = Device(
        user_id=current_user.id,
        device_name=device.name,
        application_code=device.application_code,
        secret_key=device.secret_key
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return {"message": "Device added successfully", "device_id": new_device.id}

@router.get("/devices", response_model=List[DeviceOut])
def list_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    devices = db.query(Device).filter(Device.user_id == current_user.id).all()
    return [
        DeviceOut(id=d.id, name=d.device_name, application_code=d.application_code)
        for d in devices
    ]
