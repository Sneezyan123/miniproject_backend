from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from dtos import user_dto
from database.database import get_db
from fastapi import Depends, HTTPException
from models.role import RoleEnum
from services.hash import hash_password, verify_password
from sqlalchemy import select
from dtos.profile_dto import ProfileUpdate
from sqlalchemy.orm import joinedload

async def create_user(user: user_dto.User, db: AsyncSession):
    # Run email check in async context
    existing_user = await get_user_by_email(user.email, db)
    if existing_user:
        return None
        
    role_map = {
        RoleEnum.user: 2,
        RoleEnum.admin: 1,
        RoleEnum.logistician: 3
    }
    role_id = role_map.get(user.role, 2)

    new_user = User(email=user.email,
                    password=hash_password(user.password),
                    role_id=role_id,
                    avatar=user.avatar)
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        # Load role relationship explicitly
        stmt = select(User).options(joinedload(User.role)).filter(User.id == new_user.id)
        result = await db.execute(stmt)
        return result.unique().scalar_one()
    except Exception as e:
        await db.rollback()
        raise e

async def get_user_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .options(joinedload(User.role))
        .where(User.id == id)
    )
    return result.unique().scalar_one_or_none()

async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .options(joinedload(User.role))
        .where(User.email == email)
    )
    return result.unique().scalar_one_or_none()

async def update_user_profile(
    user_id: int,
    profile_data: ProfileUpdate,
    db: AsyncSession
) -> User:
    user = await get_user_by_id(user_id, db)
    if not user:
        return None
        
    if profile_data.email:
        existing_user = await get_user_by_email(profile_data.email, db)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = profile_data.email
        
    if profile_data.avatar_url is not None:
        user.avatar = profile_data.avatar_url

    await db.commit()
    await db.refresh(user)
    return user

async def change_user_password(
    user_id: int,
    current_password: str,
    new_password: str,
    db: AsyncSession
) -> bool:
    user = await get_user_by_id(user_id, db)
    if not user or not verify_password(current_password, user.password):
        return False
        
    user.password = hash_password(new_password)
    await db.commit()
    return True