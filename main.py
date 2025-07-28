# Import fastapi
from fastapi import FastAPI, HTTPException

# Using Streaming Response here so that binary files can be streamed to client
# In this the QR image
from fastapi.responses import StreamingResponse

# Normal response, if client doesn't support streaming response
# from fastapi.responses import Response

# Python is dynamically typed so to avoid surprises
# Adding Pydantic to fix a predefined schema
# This allows us to write contrainsts and ensure its conforms to it
from pydantic import BaseModel

# To work with hitting endpoints
import requests

# To generate QR Code from the hex string
import qrcode

# To work with files as Objects
from io import BytesIO
import io

# To deal with generating unique references and hashing
import hashlib
import hmac
import time
import random

# To read and load environment files
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create the instance of FastAPI App
app = FastAPI()

# Request Model for /generate-qr endpoint
class QRRequest(BaseModel):
    # Payment amount to generate QR for
    amount: float  

# Helper function : Generate unique reference ID
# Format: REF<timestamp><4-digit-random-number>
# Example: REF17221358481234
def generate_unique_reference_id():
    # Current Unix time
    timestamp = int(time.time())  
    # 4-digit random number
    random_num = random.randint(1000, 9999)  
    return f"REF{timestamp}{random_num}"

# Helper function : Generate QR via FIUU API
def generate_QR(data: str) -> bytes:
    '''
    Generate a QR code image as PNG bytes from input hex string data
    Args : 
        data (str) : hex string information to encode within the QR Code
    Returns : 
        bytes : they PNG image data representing the QR Code
    Raises : 
        ValueError: If the input data is invalid or empty
    '''

    # Intialize the QR Object for generating the QR Code
    '''
    version : Integer parameter from 1 to 40 to control the QR Size, 1 being the 21 x 21 matrix
    error_correction : controls error correction for QR (inserts redudant data to recover QR if lost) - L (7% can be corrected)
    box_size : pixel size of each QR dot
    border : thickness of the border in boxes
    '''
    QR = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_L, 
        box_size = 10,
        border = 4
    )
    
    # Add the payload data to the object
    QR.add_data(data)

    # Construct the QR matrix and fit the content
    # fit = True ensures the best fit size automatically
    QR.make(fit=True)
    
    # Black squares + white background spaces
    # Convert to RGB to provide support for image processing comapatibility
    # Image itself is Black and white
    qr_image = QR.make_image(fill_color="black", back_color="white").convert('RGB')

    # Create a byte array object and save the QR image in PNG format
    byte_arr = BytesIO()
    qr_image.save(byte_arr, format='PNG')

    # Return its byte content
    return byte_arr.getvalue()

# Define the endpoint
@app.get("/generate-qr")
async def get_QR_code(amount: float):
    '''
    Generates and returns a QR code image based on the provided data
    Args : 
        float: the amount to paid
    Returns : 
        bytes : they PNG image data representing the QR Code
    Raises : 
        HTTPException: If the input data is invalid or empty
    '''

    # Load up the env variables
    # Ensure there are fallbacks setup so we don't end up with None
    application_code = os.getenv("OPA_APP_CODE")  or "<your_app_code>"
    secret_key = os.getenv("OPA_SECRET_KEY") or "<your_secret_key>"


    # Check if data parameter is empty
    if not amount:
        # Raise 400 status code HTTP Exception
        raise HTTPException(status_code = 400, detail = "'amount' query parameter cannot be empty.")
    
    # Standard fixed values
    version = "V3"
    channel_id = "24"
    currency_code = "MYR"
    store_id = "nextmachines01"
    terminal_id = "1"

    # Required by the api to hash it with hmac-sha256 algorithm
    hash_type = "hmac-sha256"

    # Get a unique reference id for the transaction
    reference_id = generate_unique_reference_id()

    # Construct parameters required by FIUU
    params = {
        # Cast amount to string
        "amount": str(amount),
        "applicationCode": application_code,
        "channelId": channel_id,
        "currencyCode": currency_code,
        "hashType": hash_type,
        "referenceId": reference_id,
        "storeId": store_id,
        "terminalId": terminal_id,
        "version": version
    }

    try:
        # Get the QR Code
        qr_image_bytes = generate_QR(data)

        # Wrap the raw bytes data representing a PNG into BytesIO Object
        # This creates an in-memory binary stream

        # If client doesn't support streaming respone, use this
        # return Response(content=qr_image_bytes, media_type="image/png")

        # Then stream the content of the binary stream back to the client as HTTP Response
        return StreamingResponse(io.BytesIO(qr_image_bytes), media_type="image/png")
    
    except Exception as e:
        print(f"Error generating QR Code : {e}")
        raise HTTPException(status_code = 500, detail = "Failed to generate a QR code image.")
    
if __name__ == "__main__":
    # python -m uvicorn main:app --reload
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8080)