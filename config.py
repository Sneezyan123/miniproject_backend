from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    ASYNC_DATABASE_URI: str = None  # Add this for alembic migrations
    EXPIRES_IN: int
    FACE_API_KEY: str
    FACE_API_URL: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure async URI is set for migrations
        if not self.ASYNC_DATABASE_URI and self.DATABASE_URL:
            self.ASYNC_DATABASE_URI = self.DATABASE_URL

    class Config:
        env_file = ".env"

settings = Settings()
