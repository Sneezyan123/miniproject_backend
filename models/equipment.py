from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from database.database import Base
from enum import Enum as PyEnum

class PurposeEnum(PyEnum):
    weapon = "weapon"
    humanitarian = "humanitarian" 
    vehicle = "vehicle"

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True)
    img_url = Column(String)
    description = Column(String)
    detailed_description = Column(String)
    purpose = Column(Enum(PurposeEnum), nullable=False)
    quantity = Column(Integer, default=0)
    user_quantities = relationship("UserEquipment", back_populates="equipment")
