from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
from models.equipment import Equipment
from models.user_equipment import UserEquipment
from dtos.equipment_dto import EquipmentBase

from openai import OpenAI
import openai
import requests
from config import settings

async def create_equipment(equipment: EquipmentBase, db: AsyncSession):
    # Convert DTO to dict and create equipment
    equipment_data = equipment.model_dump(exclude_unset=True)
    db_equipment = Equipment(**equipment_data)
    db.add(db_equipment)
    await db.commit()
    await db.refresh(db_equipment)
    return db_equipment

async def get_all_equipment(db: AsyncSession):
    result = await db.execute(select(Equipment))
    return result.scalars().all()

async def get_equipment_by_id(equipment_id: int, db: AsyncSession):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    return result.scalar_one_or_none()

async def delete_equipment(equipment_id: int, db: AsyncSession):
    query = delete(Equipment).where(Equipment.id == equipment_id)
    await db.execute(query)
    await db.commit()
    return True

async def get_equipment_by_user_id(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(UserEquipment)
        .options(joinedload(UserEquipment.equipment))
        .filter(UserEquipment.user_id == user_id)
    )
    return result.scalars().all()

async def get_free_equipment(db: AsyncSession):
    result = await db.execute(
        select(Equipment)
        .where(~Equipment.owners.any())  # Select equipment with no owners
    )
    return result.scalars().all()

async def generate_ai_description(name: str, purpose: str) -> str:
    try:
        api_key = settings.FACE_API_KEY
        api_url = settings.FACE_API_URL
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload={
            "messages": [
                {
                    "role": "user",
                    "content": f"Generate a description for military equipment with the following details:\nName: {name}\nPurpose: {purpose} in Ukrainian language. First of all, write small general information then characteristics, then write about the purpose of the equipment."
                }
            ],
            "model": "deepseek/deepseek-v3-0324",
        }
        response = requests.post(api_url, headers=headers, json=payload)
        return response.json().get("choices")[0].get("message").get("content")
    except Exception as e:
        raise Exception(f"Failed to generate AI description: {str(e)}")

async def update_equipment(equipment_id: int, equipment: EquipmentBase, db: AsyncSession):
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    db_equipment = result.scalar_one_or_none()
    if db_equipment:
        for key, value in equipment.model_dump(exclude_unset=True).items():
            setattr(db_equipment, key, value)
        await db.commit()
        await db.refresh(db_equipment)
    return db_equipment

async def assign_equipment_to_user(equipment_id: int, user_id: int, quantity: int, db: AsyncSession):
    equipment = await get_equipment_by_id(equipment_id, db)
    if equipment and equipment.quantity >= quantity:
        user_equipment = UserEquipment(
            equipment_id=equipment_id,
            user_id=user_id,
            quantity=quantity
        )
        equipment.quantity -= quantity
        db.add(user_equipment)
        await db.commit()
        await db.refresh(equipment)
        return True
    return False

async def get_user_equipment_quantity(user_id: int, equipment_id: int, db: AsyncSession):
    result = await db.execute(
        select(UserEquipment)
        .filter(
            UserEquipment.user_id == user_id,
            UserEquipment.equipment_id == equipment_id
        )
    )
    user_equipment = result.scalar_one_or_none()
    return user_equipment.quantity if user_equipment else 0

async def update_user_equipment_quantity(user_id: int, equipment_id: int, new_quantity: int, db: AsyncSession):
    result = await db.execute(
        select(UserEquipment)
        .filter(
            UserEquipment.user_id == user_id,
            UserEquipment.equipment_id == equipment_id
        )
    )
    user_equipment = result.scalar_one_or_none()
    if user_equipment:
        equipment = await get_equipment_by_id(equipment_id, db)
        quantity_diff = new_quantity - user_equipment.quantity
        if equipment.quantity >= quantity_diff:
            equipment.quantity -= quantity_diff
            user_equipment.quantity = new_quantity
            await db.commit()
            return True
    return False