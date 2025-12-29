from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test_flabs2fabs.db"  # Default fallback
    JWT_SECRET: str = "super-secret-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_USERNAME: str = "admin"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

settings = Settings()
