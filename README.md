# 🚀 FIUU QR Payment Generator – FastAPI Integration

A simple FastAPI service to generate **DuitNow QR codes** using the **FIUU Payment Gateway**. This service generates a secure HMAC-SHA256 signature, makes a request to the FIUU API, and streams back the QR image as a response.

---

## Features

- Generate HMAC-SHA256 signature from sorted parameters
- Send payment request to FIUU API
- Return static QR code as `image/png` stream using DuitNow QR Channel

---

## Last Tested Environment

- **Python Version:** `3.12.8`

## Install Dependencies

`pip install -r requirements.txt`

## .env format

```
OPA_APP_CODE=your_fiuu_application_code
OPA_SECRET_KEY=your_fiuu_secret_key
```
## Run the server

`python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload`

## API Usage

### Request

POST /generate-qr
```json
{
  "amount": 25.00
}
```
### Response

- Returns the QR code as an image:
- Content-Type: image/png
- Streams the PNG image directly in response

## Folder Strucuture
.  
├── main.py              # FastAPI application with QR logic  
├── .env                 # FIUU credentials  
├── requirements.txt     # Python dependencies  
└── README.md            # Documentation  

---

