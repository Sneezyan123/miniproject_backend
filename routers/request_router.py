from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from services import request_service
from dtos.request_dto import RequestCreate, RequestUpdate, RequestResponse
from models.user import User
from authentication.auth import get_current_user
from models.role import RoleEnum

router = APIRouter()

@router.post("/", response_model=RequestResponse)
async def create_request(
    request: RequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    print(f"reQWOEQWEKQOWEKOQquest: {request}")
    return await request_service.create_request(request, current_user.id, db)

@router.get("/my", response_model=list[RequestResponse])
async def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        requests = await request_service.get_user_requests(current_user.id, db)
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending", response_model=list[RequestResponse])
async def get_pending_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role_id != 3:  # Check for logistician role
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        requests = await request_service.get_pending_requests(db)
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approved", response_model=list[RequestResponse])
async def get_approved_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role_id != 3:  # Check for logistician role
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        requests = await request_service.get_approved_requests(db)
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{request_id}", response_model=RequestResponse)
async def update_request_status(
    request_id: int,
    request_update: RequestUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role.name != RoleEnum.logistician:
        raise HTTPException(status_code=403, detail="Not authorized")
    return await request_service.update_request_status(request_id, request_update.status, db)

@router.post("/request-many")
async def create_requests(
    requests: list[RequestCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    for request in requests:
        await request_service.create_request(request, current_user.id, db)
    return {"message": "Requests created successfully"}

@router.get("/{request_id}", response_model=RequestResponse)
async def get_request_by_id(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    request = await request_service.get_request_by_id(request_id, db)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check if user has access to this request
    if current_user.role_id != 3 and request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this request")
        
    return request

@router.delete("/{request_id}")
async def delete_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    request = await request_service.get_request_by_id(request_id, db)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.user_id != current_user.id and current_user.role_id != 3:
        raise HTTPException(status_code=403, detail="Not authorized to delete this request")
        
    if await request_service.delete_request(request_id, db):
        return {"message": "Request deleted successfully"}
    raise HTTPException(status_code=404, detail="Request not found")
@router.get("/all")
async def get_all_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        
        requests = await request_service.get_all_requests(db)
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))