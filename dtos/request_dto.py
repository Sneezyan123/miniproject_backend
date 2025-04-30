from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from models.request import RequestStatus, RequestPriority

class RequestItemCreate(BaseModel):
    equipment_id: int
    quantity: int

class RequestCreate(BaseModel):
    description: Optional[str] = None
    priority: RequestPriority = RequestPriority.medium  # Add this line
    items: List[RequestItemCreate]

class RequestUpdate(BaseModel):
    status: RequestStatus

class EquipmentInfo(BaseModel):
    id: int
    name: str
    img_url: Optional[str] = None
    description: Optional[str] = None

class RequestItemResponse(BaseModel):
    id: int
    equipment_id: int
    quantity: int
    status: RequestStatus
    created_at: datetime
    equipment: Optional[EquipmentInfo] = None

class RequestResponse(BaseModel):
    id: int
    description: Optional[str]
    priority: RequestPriority  # Add this line
    created_at: datetime
    updated_at: datetime
    user_id: int
    items: List[RequestItemResponse]
