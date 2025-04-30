from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class UserEquipment(Base):
    __tablename__ = "equipment_owners"
    equipment_id = Column(Integer, ForeignKey('equipment.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    quantity = Column(Integer, default=0)
    equipment = relationship("Equipment", back_populates="user_quantities")
    user = relationship("User", back_populates="equipment_quantities")
