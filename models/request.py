from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
from enum import Enum as PyEnum
from datetime import datetime

class RequestStatus(PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class RequestPriority(PyEnum):
    low = "low"
    medium = "medium" 
    high = "high"
    critical = "critical"

class EquipmentRequest(Base):
    __tablename__ = "equipment_requests"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String)
    priority = Column(Enum(RequestPriority), default=RequestPriority.medium)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(
        "User",
        lazy="selectin",
        backref="equipment_requests"
    )
    items = relationship(
        "RequestItem",
        back_populates="request",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
