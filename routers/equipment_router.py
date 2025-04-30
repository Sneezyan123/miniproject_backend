from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from services import equipment_service
from dtos.equipment_dto import EquipmentBase, EquipmentAIRequest
from models.user import User
from authentication.auth import get_current_user

router = APIRouter()

@router.post("/")
async def create_equipment(
    equipment: EquipmentBase, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    db_equipment = await equipment_service.create_equipment(equipment, db)
    
    return db_equipment

@router.get("/")
async def get_equipment(db: AsyncSession = Depends(get_db)):
    return await equipment_service.get_all_equipment(db)

@router.get("/{equipment_id}")
async def get_equipment_by_id(equipment_id: int, db: AsyncSession = Depends(get_db)):
    equipment = await equipment_service.get_equipment_by_id(equipment_id, db)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.delete("/{equipment_id}")
async def delete_equipment(equipment_id: int, db: AsyncSession = Depends(get_db)):
    if not await equipment_service.delete_equipment(equipment_id, db):
        raise HTTPException(status_code=404, detail="Equipment not found")
    return {"message": "Equipment deleted successfully"}

@router.put("/{equipment_id}")
async def update_equipment(
    equipment_id: int, 
    equipment: EquipmentBase,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated_equipment = await equipment_service.update_equipment(equipment_id, equipment, db)
    if not updated_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return updated_equipment

@router.get("/user/equipment")
async def get_current_user_equipment(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    equipment = await equipment_service.get_equipment_by_user_id(current_user.id, db)
    return equipment

@router.get("/free")
async def get_free_equipment(db: AsyncSession = Depends(get_db)):
    return await equipment_service.get_free_equipment(db)

@router.post("/generate-description")
async def generate_description(
    request: EquipmentAIRequest,
):
    try:
        description = await equipment_service.generate_ai_description(
            request.name,
            request.purpose
        )
        return {"detailed_description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
