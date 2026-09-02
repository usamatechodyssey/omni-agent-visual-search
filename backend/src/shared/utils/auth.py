import secrets
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from backend.src.core.config import settings

# Password Hasher
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def generate_api_key():
    random_string = secrets.token_urlsafe(32)
    return f"omni_{random_string}"

# ------------------- 🔒 STRICT SUPER ADMIN CHECK -------------------
def is_super_admin(email: str, password: str) -> bool:
    """
    Sirf configure kiye gaye SUPER_ADMIN_EMAIL aur password ko allow karega.
    Baaki sab emails/passwords ke liye False return karega.
    """
    # Email check
    if email != settings.SUPER_ADMIN_EMAIL:
        return False
    # Password Hash check (Argon2)
    if not settings.SUPER_ADMIN_PASSWORD_HASH:
        print("⚠️ ERROR: SUPER_ADMIN_PASSWORD_HASH .env mein set nahi hai!")
        return False
    return verify_password(password, settings.SUPER_ADMIN_PASSWORD_HASH)