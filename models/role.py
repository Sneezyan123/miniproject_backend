from database.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from enum import Enum

class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"
    logistician = "logistician"

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True)
    user = relationship("User", back_populates="role")