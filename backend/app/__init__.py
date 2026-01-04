import os

from fastapi.security import HTTPBearer

SECRET = os.getenv("JWT_SECRET")
security = HTTPBearer()
DATABASE_URL = os.getenv("DATABASE_URL")
