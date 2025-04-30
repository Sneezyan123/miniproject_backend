from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from services import user_service
from models.user import User
from database.database import get_db
from fastapi import Depends
from typing import Annotated
from fastapi import HTTPException
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
import database.database as db_dependency
from services.hash import verify_password
import jwt
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.EXPIRES_IN
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
async def authenticate_user(email, password: str, db: db_dependency):
    user = await user_service.get_user_by_email(email, db)
    if not user or not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_access_token(user):
    token = create_access_token(data={"id":user.id})
    return token
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userid: int = int(payload.get("id"))
        if userid is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = await user_service.get_user_by_id(userid, db)
    if user is None:
        raise credentials_exception
    return user