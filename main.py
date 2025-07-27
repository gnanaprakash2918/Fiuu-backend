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