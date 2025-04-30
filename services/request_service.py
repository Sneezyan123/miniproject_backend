from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models.request import EquipmentRequest, RequestStatus
from models.request_item import RequestItem
from dtos.request_dto import RequestCreate
from models.user_equipment import UserEquipment

async def create_request(request: RequestCreate, user_id: int, db: AsyncSession):
    try:
        db_request = EquipmentRequest(
            user_id=user_id,
            description=request.description,
            priority=request.priority
        )
        
        for item in request.items:
            request_item = RequestItem(
                equipment_id=item.equipment_id,
                quantity=item.quantity
            )
            db_request.items.append(request_item)
        
        db.add(db_request)
        await db.commit()
        
        # Refresh the instance to load relationships
        await db.refresh(db_request)
        
        # Explicitly load the relationships
        for item in db_request.items:
            await db.refresh(item)
            await db.refresh(item.equipment)
            
        return db_request
    except Exception as e:
        await db.rollback()
        raise e

async def get_user_requests(user_id: int, db: AsyncSession):
    query = (
        select(EquipmentRequest)
        .options(
            joinedload(EquipmentRequest.items).joinedload(RequestItem.equipment)
        )
        .filter(EquipmentRequest.user_id == user_id)
    )
    result = await db.execute(query)
    return result.unique().scalars().all()

async def get_pending_requests(db: AsyncSession):
    query = (
        select(EquipmentRequest)
        .options(
            joinedload(EquipmentRequest.items).joinedload(RequestItem.equipment)
        )
        .join(RequestItem)
        .filter(RequestItem.status == RequestStatus.pending)
        .distinct()
    )
    result = await db.execute(query)
    return result.unique().scalars().all()

async def get_approved_requests(db: AsyncSession):
    query = (
        select(EquipmentRequest)
        .options(
            joinedload(EquipmentRequest.items).joinedload(RequestItem.equipment)
        )
        .join(RequestItem)
        .filter(RequestItem.status == RequestStatus.approved)
        .distinct()
    )
    result = await db.execute(query)
    return result.unique().scalars().all()

async def get_request_by_id(request_id: int, db: AsyncSession):
    query = (
        select(EquipmentRequest)
        .options(joinedload(EquipmentRequest.items).joinedload(RequestItem.equipment))
        .filter(EquipmentRequest.id == request_id)
    )
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()

async def update_request_status(request_id: int, status: RequestStatus, db: AsyncSession):
    result = await db.execute(
        select(EquipmentRequest)
        .options(
            joinedload(EquipmentRequest.items).joinedload(RequestItem.equipment)
        )
        .filter(EquipmentRequest.id == request_id)
    )
    request = result.unique().scalar_one_or_none()
    
    if request:
        for item in request.items:
            item.status = status
            if status == RequestStatus.approved and item.equipment:
                # Check if user already has this equipment
                user_equipment = await db.execute(
                    select(UserEquipment)
                    .filter(
                        UserEquipment.user_id == request.user_id,
                        UserEquipment.equipment_id == item.equipment_id
                    )
                )
                existing = user_equipment.scalar_one_or_none()
                
                if existing:
                    existing.quantity += item.quantity
                    item.equipment.quantity -= item.quantity
                else:
                    new_user_equipment = UserEquipment(
                        user_id=request.user_id,
                        equipment_id=item.equipment_id,
                        quantity=item.quantity
                    )
                    db.add(new_user_equipment)
                    item.equipment.quantity -= item.quantity
        
        await db.commit()
        
        # Refresh relationships after commit
        result = await db.execute(
            select(EquipmentRequest)
            .options(
                joinedload(EquipmentRequest.items).joinedload(RequestItem.equipment)
            )
            .filter(EquipmentRequest.id == request_id)
        )
        request = result.unique().scalar_one_or_none()
    return request

async def delete_request(request_id: int, db: AsyncSession):
    result = await db.execute(
        select(EquipmentRequest).where(EquipmentRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if request:
        await db.delete(request)
        await db.commit()
        return True
    return False

async def get_all_requests(db: AsyncSession):
    query = (
        select(EquipmentRequest)
        .options(
            joinedload(EquipmentRequest.items).joinedload(RequestItem.equipment)
        )
    )
    result = await db.execute(query)
    return result.unique().scalars().all()