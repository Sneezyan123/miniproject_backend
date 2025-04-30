from pydantic import BaseModel, EmailStr

class ProfileUpdate(BaseModel):
    email: EmailStr | None = None
    avatar_url: str | None = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
