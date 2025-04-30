from pydantic import BaseModel, EmailStr, Field
from models.role import RoleEnum
class User(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: RoleEnum = "user"
    avatar: str = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"