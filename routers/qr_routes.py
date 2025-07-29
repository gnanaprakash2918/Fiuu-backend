from fastapi import APIRouter, HTTPException

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

# To work with files as Objects
from io import BytesIO
import io

# To deal with generating unique references and hashing
import hashlib
import hmac

# To read and load environment files
import os
from dotenv import load_dotenv

# uuid for Reference number generation
import uuid

# Load environment variables from .env file
load_dotenv()

# Create A Router
router = APIRouter()

# Request Model for /generate-qr endpoint
class QRRequest(BaseModel):
    # Payment amount to generate QR for
    amount: float  

# Helper function : Generate unique reference ID using UUID4
# Format: REF<UUID> (without hyphens)
# Example: REF550e8400e29b41d4a716446655440000
def generate_unique_reference_id():
    return f"REF{uuid.uuid4().hex.upper()}"


# Helper Function : Generate HMAC-SHA256 Signature
def generate_signature(params: dict, secret_key: str) -> str:
    # Sanitize and fill missing fields with empty string for consistent hashing
    full_params = {
        "amount": params.get("amount", ""),
        "applicationCode": params.get("applicationCode", ""),
        "businessDate": params.get("businessDate", ""),
        "channelId": params.get("channelId", ""),
        "currencyCode": params.get("currencyCode", ""),
        "description": params.get("description", ""),
        "hashType": params.get("hashType", ""),
        "imageFormat": params.get("imageFormat", ""),
        "imageSize": params.get("imageSize", ""),
        "referenceId": params.get("referenceId", ""),
        "storeId": params.get("storeId", ""),
        "terminalId": params.get("terminalId", ""),
        "validityDuration": params.get("validityDuration", ""),
        "metadata": params.get("metadata", ""),
        "version": params.get("version", "")
    }

    # Sort keys and concatenate values
    # Go through every key in sorted keys and concat them to a string
    # this is required to generate the hash
    # Generate the HMAC-SHA256 Signature using sorted param values
    sorted_keys = sorted(full_params.keys())
    concatenated = ''.join(full_params[k] for k in sorted_keys)

    # Create HMAC SHA256 signature
    return hmac.new(secret_key.encode(), concatenated.encode(), hashlib.sha256).hexdigest()

# Helper function : Generate QR via FIUU API
def generate_qr(amount: float) -> bytes:
    # Load up the env variables
    # Ensure there are fallbacks setup so we don't end up with None
    application_code = os.getenv("OPA_APP_CODE")  or "<your_app_code>"
    secret_key = os.getenv("OPA_SECRET_KEY") or "<your_secret_key>"

    # If they application_code or secret_key is not set, raise 500 exception
    if not application_code or not secret_key:
         raise HTTPException(status_code = 500, detail = "Merchant credentials not set")
    
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
        "amount": f"{amount:.2f}",
        "applicationCode": application_code,
        "channelId": channel_id,
        "currencyCode": currency_code,
        "hashType": hash_type,
        "referenceId": reference_id,
        "storeId": store_id,
        "terminalId": terminal_id,
        "version": version,        

        # Optional/empty fields from Postman pre-request logic
        "businessDate": "",
        "description": "",
        "imageFormat": "",
        "imageSize": "",
        "validityDuration": "",
        "metadata": ""
    }

    signature = generate_signature(params, secret_key)
    # Add generated HMAC to the payload
    payload = params.copy()
    payload["signature"] = signature

    # Set endpoint and headers
    api_endpoint = "https://opa.fiuu.com/RMS/API/MOLOPA/precreate.php"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        # Send the request to FIUU endpoint
        response = requests.post(
            api_endpoint, 
            headers = headers, 
            data = payload,
            timeout = 10
        )

        # If HTTP request failed
        if response.status_code != 200:
            raise HTTPException(
                status_code = response.status_code,
                detail = f"FIUU API Error: {response.text}"
            )
        # Parse the response JSON
        try:
            response_data = response.json()
        
        except ValueError:
            return {"error": "Invalid JSON from FIUU API", "raw": response.text}

        # Return the response with empty string fallbacks
        return {    
            "qr_url": response_data.get("imageUrl", ""),
            "transaction_id": response_data.get("molTransactionId", ""),
            "status": response_data.get("statusCode", ""),
            "amount": response_data.get("amount", ""),
            "currency": response_data.get("currencyCode", "")
        }
    
    except Exception as e:
        print(f"Error generating QR Code : {e}")
        raise HTTPException(
            status_code = response.status_code,
            detail = f"FIUU API Error: {response.text}"
        )    
    

# Define the endpoint
@router.post("/generate-qr")
async def get_QR_code(request: QRRequest):
    '''
    Generates and returns a QR code image based on the provided data
    Args : 
        float: the amount to paid
    Returns : 
        JSON Response : Generated QR Link, transaction_id, status, amount, currency
    Raises : 
        HTTPException: If the input data is invalid or empty
    '''
    # Validate amount
    # Check if data parameter is empty
    if not request.amount:
        # Raise 400 status code HTTP Exception
        raise HTTPException(status_code = 400, detail = "'amount' query parameter cannot be empty.")
    
    if request.amount <= 0:
        raise HTTPException(status_code = 400, detail = "Amount must be greater than 0")
    
    # Generate and return QR
    result = generate_qr(request.amount)
    img_data = requests.get(result["qr_url"]).content
    return StreamingResponse(io.BytesIO(img_data), media_type="image/png")
