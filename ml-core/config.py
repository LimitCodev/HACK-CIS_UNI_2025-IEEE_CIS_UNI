import os
from pathlib import Path


class Settings:
    PROJECT_NAME: str = "HACK[CIS] UNI 2025"
    VERSION: str = "1.0.0"
    
    BASE_DIR: Path = Path(__file__).resolve().parent
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres123@localhost:5432/hackcis"
    )
    
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379"
    )
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o")
    FALLBACK_LLM_MODEL: str = "gpt-4o-mini"
    
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "3000"))
    CHUNK_OVERLAP: int = 200
    
    CACHE_TTL_SUMMARY: int = 3600
    CACHE_TTL_QUIZ: int = 1800
    
    MAX_FILE_SIZE_MB: int = 50
    MAX_VIDEO_DURATION_MINUTES: int = 120
    
    SUPPORTED_PDF_EXTENSIONS: list[str] = [".pdf"]
    SUPPORTED_VIDEO_PLATFORMS: list[str] = ["youtube.com", "youtu.be"]
    
    SESSION_CLEANUP_DAYS: int = 30
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            raise ValueError("Al menos una API key de LLM debe estar configurada")
        
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL es requerido")
        
        cls.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.validate()