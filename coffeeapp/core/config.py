from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Coffee Shop API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "coffee_shop"
    
    JWT_SECRET_KEY: str = "hikamoruru"  # в продакшене использовать безопасный ключ
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Добавляем новые настройки
    FRONTEND_HOST: str = "http://localhost:3000"  # URL фронтенда
    ALLOWED_HOSTS: str = "*"  # Изменено с list на str
    SECRET_KEY: str = "your-secret-key-for-csrf"  # Для CSRF защиты
    
    ENVIRONMENT: str = "development"  # development или production
    
    class Config:
        env_file = ".env"

settings = Settings() 