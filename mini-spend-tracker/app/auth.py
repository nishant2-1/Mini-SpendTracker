import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def require_api_key(api_key: str = Security(api_key_header)):
    expected_key = os.getenv("API_KEY", "secret-api-key")
    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key

# Alias in case another module looks for get_api_key
get_api_key = require_api_key
