from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt

from app import SECRET


def hash_password(password: str) -> str:
    """Хеширует пароль с помощью bcrypt"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Проверяет пароль против хеша"""
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_token(username: str) -> str:
    if SECRET is None:
        raise ValueError("JWT_SECRET environment variable is not set")
    payload = {"sub": username, "exp": datetime.now(UTC) + timedelta(hours=2)}
    return jwt.encode(payload, SECRET, algorithm="HS256")
