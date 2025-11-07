import os
from pathlib import Path

class Settings:
    PROJECT_NAME: str = "HACK[CIS] UNI 2025"
    VERSION: str = "1.0.0"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")
    
    ML_CORE_URL: str = os.getenv("ML_CORE_URL", "http://ml_core:8001")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-dev")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    
    SUPPORTED_PDF_EXTENSIONS: list[str] = ["application/pdf"]
    SUPPORTED_VIDEO_PLATFORMS: list[str] = ["youtube.com", "youtu.be"]
    
    @classmethod
    def validate(cls):
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL es requerido.")
        
        if not cls.REDIS_URL:
            raise ValueError("REDIS_URL es requerido.")

        cls.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.validate()