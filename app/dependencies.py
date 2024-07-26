from fastapi import Header, HTTPException
from config import settings

def verify_token(x_token: str = Header(...)):
    if x_token != settings.STATIC_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
