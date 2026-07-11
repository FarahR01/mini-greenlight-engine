import os
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GREENLIGHT_API_KEY")

def verify_api_key(x_api_key: str = Header(..., description="API key required to access this endpoint")):
    if not API_KEY:
        # Fail closed: if no key is configured server-side, refuse everything
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: no API key configured"
        )
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return True