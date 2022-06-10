from fastapi import Security, HTTPException
from fastapi.security import HTTPBasic
from fastapi.security import APIKeyHeader
from starlette import status

from .config import settings_access_control

basic_auth = HTTPBasic()
api_key_header_auth = APIKeyHeader(name="key", auto_error=True)


async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header != settings_access_control.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
