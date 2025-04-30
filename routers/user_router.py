from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from typing import Annotated
from services import user_service
from dtos import user_dto
from dtos.profile_dto import ProfileUpdate, PasswordChange
from models.user import User
from authentication.auth import authenticate_user, get_access_token, get_current_user

router = APIRouter()

db_dependency = Annotated[AsyncSession, Depends(get_db)]

@router.post("/register")
async def create(data: user_dto.User, db: db_dependency):
    user = await user_service.create_user(data, db)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = get_access_token(user)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.name,
            "avatar": user.avatar
        }
    }

@router.post("/login")
async def login(user_dto: user_dto.User, db: db_dependency):
    user: User = await authenticate_user(user_dto.email, user_dto.password, db)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = get_access_token(user)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.name,
            "avatar": user.avatar
        }
    }

@router.post("/profile")
async def protected(user: User = Depends(get_current_user)):
    return user

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await user_service.get_user_by_id(current_user.id, db)
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.name,
        "avatar": user.avatar
    }

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated_user = await user_service.update_user_profile(
        current_user.id,
        profile_data,
        db
    )
    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "role": updated_user.role.name,
        "avatar_url": updated_user.avatar
    }

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await user_service.change_user_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password,
        db
    )
    if not success:
        raise HTTPException(status_code=400, detail="Invalid current password")
    return {"message": "Password changed successfully"}