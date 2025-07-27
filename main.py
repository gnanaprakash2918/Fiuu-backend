# Import fastapi
from fastapi import FastAPI, HTTPException

# Using Streaming Response here so that binary files can be streamed to client
# In this the QR image
from fastapi.responses import StreamingResponse

# To generate QR Code from the hex string
import qrcode

# To work with files as Objects
from io import BytesIO


# Create the instance of FastAPI App
app = FastAPI()

def generate_QR(data: str) -> bytes:
    '''
    The function takes in a hex-string and expected to return a sequence of bytes
    The byte data here represents the generated QR Code as (PNG Format)
    '''