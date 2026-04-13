from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_database
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models.schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, db=Depends(get_database)):
    existing_user = await db.users.find_one({"email": payload.email.lower()})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user_id = str(uuid4())
    user_doc = {
        "_id": user_id,
        "email": payload.email.lower(),
        "full_name": payload.full_name,
        "password_hash": hash_password(payload.password),
        "role": "operator",
        "created_at": datetime.now(timezone.utc),
    }
    await db.users.insert_one(user_doc)

    access_token = create_access_token(user_id)
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user_id,
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            role=user_doc["role"],
        ),
    )


@auth_router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db=Depends(get_database)):
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(user["_id"])
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user["_id"],
            email=user["email"],
            full_name=user.get("full_name", ""),
            role=user.get("role", "operator"),
        ),
    )


@auth_router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        full_name=current_user.get("full_name", ""),
        role=current_user.get("role", "operator"),
    )
