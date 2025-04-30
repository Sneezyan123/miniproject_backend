from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    EXPIRES_IN: int
    FACE_API_KEY: str
    FACE_API_URL: str
    class Config:
        env_file = ".env"  # Load variables from .env file

settings = Settings()
