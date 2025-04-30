from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    avatar = Column(String, nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship("Role", back_populates="user", uselist=False)
    equipment_quantities = relationship("UserEquipment", back_populates="user")