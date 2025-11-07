import asyncio
from fastapi import FastAPI, Depends, Request, HTTPException, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession

from database.db_manager import DatabaseManager
from database.session_handler import SessionHandler
from database.models import Base
from services.summarizer_service import SummarizerService
from core.config import settings
from api.v1.analyze_routes import router as analyze_router

# --- Inicialización de FastAPI ---

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# --- Inicialización de Servicios ---

db_manager = DatabaseManager()
summarizer_service = SummarizerService()

# --- Middleware CORS ---

origins = settings.CORS_ORIGINS.split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependencia de Sesión de BD (Inyección de Dependencias) ---

def get_db():
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

# --- Eventos de Inicio y Fin ---

@app.on_event("startup")
def startup_event():
    print("Iniciando aplicación y conectando a PostgreSQL...")
    db_manager.create_tables()
    print("Tablas de BD verificadas/creadas.")

@app.on_event("shutdown")
def shutdown_event():
    print("Apagando y limpiando conexiones...")
    pass

# --- Rutas de Sesión y Salud ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "db_status": "connected", "ml_service_status": "ready"}

@app.post("/session/start")
async def start_session(db: DBSession = Depends(get_db)):
    session_handler = SessionHandler(db=db, redis_client=summarizer_service.cache_manager.redis)
    session_id = session_handler.get_or_create_session()
    return {"session_id": session_id}

@app.get("/session/{session_id}/history")
async def get_history(session_id: str, db: DBSession = Depends(get_db)):
    session_handler = SessionHandler(db=db, redis_client=summarizer_service.cache_manager.redis)
    history = session_handler.get_session_history(session_id)
    return {"history": history}

# --- INCLUSIÓN DEL ROUTER MODULAR ---
# Integra todas las rutas de /api/v1 (analyze/pdf, analyze/video, generate/quiz)
app.include_router(analyze_router, prefix="/api")
# ------------------------------------