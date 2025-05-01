from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from models.request import RequestStatus, RequestPriority

class RequestItemCreate(BaseModel):
    equipment_id: int
    quantity: int

class RequestCreate(BaseModel):
    description: Optional[str] = None
    priority: RequestPriority = RequestPriority.medium
    items: List[RequestItemCreate]

class RequestUpdate(BaseModel):
    status: RequestStatus

class EquipmentInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    img_url: Optional[str] = None
    description: Optional[str] = None

class RequestItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    equipment_id: int
    quantity: int
    status: RequestStatus
    created_at: datetime
    equipment: Optional[EquipmentInfo] = None

class RequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    description: Optional[str]
    priority: RequestPriority
    created_at: datetime
    updated_at: datetime
    user_id: int
    items: List[RequestItemResponse]
