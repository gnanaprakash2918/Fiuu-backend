# Import fastapi
from fastapi import FastAPI, HTTPException

# from database import Base, engine
# from routers import auth_routes, device_routes, 
from routers import qr_routes

# Create database tables
# Base.metadata.create_all(bind=engine)

# Create the instance of FastAPI App
app = FastAPI()

# Attach routers
# app.include_router(auth_routes.router)
# app.include_router(device_routes.router)
app.include_router(qr_routes.router)

if __name__ == "__main__":
    # python -m uvicorn main:app --host localhost --port 8000 --reload
    # 127.0.0.1
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8080)