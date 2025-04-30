from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from services import equipment_service
from models.user import User
from auth.auth_bearer import JWTBearer, get_current_user
from typing import List, Any

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(JWTBearer())],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Any])
async def get_all_equipment(
    db: AsyncSession = Depends(get_db)
):
    equipment = await equipment_service.get_all_equipment(db)
    return equipment


@router.get("/category/{category}", response_model=List[Any])
async def get_equipment_by_category(
    category: str,
    db: AsyncSession = Depends(get_db)
):
    equipment = await equipment_service.get_equipment_by_category(category, db)
    return equipment


@router.get("/user", response_model=List[Any])
async def get_user_equipment(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    equipment = await equipment_service.get_equipment_by_user_id(current_user.id, db)
    return equipment