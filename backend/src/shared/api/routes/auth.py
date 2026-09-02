from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr

from backend.src.core.config import settings
from backend.src.shared.db.session import get_db
from backend.src.shared.models.user import User
from backend.src.shared.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_api_key,
    is_super_admin,  # 🔥 Strict Check Import Kiya
)
from backend.src.shared.api.routes.deps import decode_refresh_token

router = APIRouter()

# --- Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class RegistrationResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    api_key: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str


# --- 1. Registration Endpoint (🔒 Strict Lock) ---
@router.post("/auth/register", response_model=RegistrationResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # 🔥 SIRF SUPER ADMIN REGISTER KAR SAKTA HAI, BAaki SAB BLOCK
    if user_in.email != settings.SUPER_ADMIN_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled. Only Super Admin is allowed."
        )

    # Check agar email pehle se exist karta hai
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Naya User Banao + API Key Generate Karo (🔐)
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        api_key=generate_api_key(),
        allowed_domains="*"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "api_key": new_user.api_key
    }


# --- 2. Login Endpoint (🔒 Strict Super Admin Check) ---
@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # 🔥 SABSE PEHLE STRICT CHECK: Sirf configured email & password hi pass hoga
    if not is_super_admin(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied. Only Super Admin can login.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Agar Super Admin hai, toh DB se user fetch karo (taake ID aur API key mile)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    # Agar user DB mein nahi hai (pehli baar login), toh auto-create kar do
    if not user:
        new_user = User(
            email=form_data.username,
            hashed_password=get_password_hash(form_data.password),
            api_key=generate_api_key(),
            allowed_domains="*"
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        user = new_user

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


# --- 3. Refresh Token Endpoint ---
@router.post("/auth/refresh", response_model=Token)
async def refresh_token(
    data: RefreshTokenRequest,
    user: User = Depends(decode_refresh_token),
):
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }