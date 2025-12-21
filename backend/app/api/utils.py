import os
from jose import jwt, JWTError
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db import get_db
from app import security, SECRET


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if SECRET is None:
        raise ValueError("JWT_SECRET environment variable is not set")

    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
