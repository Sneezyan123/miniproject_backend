from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime
from models.request import RequestStatus

class RequestItem(Base):
    __tablename__ = "request_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("equipment_requests.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    request = relationship("EquipmentRequest", back_populates="items")
    equipment = relationship("Equipment", lazy="selectin")
