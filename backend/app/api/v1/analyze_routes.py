from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session as DBSession
from typing import Dict, Any

from ...services.summarizer_service import SummarizerService
from ...database.db_manager import DatabaseManager
from ...database.session_handler import SessionHandler
from ...database.cache_manager import CacheManager
from ...core.config import settings

# --- Inicialización y Router ---

router = APIRouter(prefix="/v1")
summarizer_service = SummarizerService()
db_manager = DatabaseManager() # Se asume que db_manager y cache_manager son singletones

# --- Dependencia de Sesión de BD ---

def get_db():
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

def get_session_handler(db: DBSession = Depends(get_db)):
    """Inyecta el manejador de sesión para acceso a BD y Cache."""
    cache_manager = CacheManager() 
    return SessionHandler(db=db, redis_client=cache_manager.redis)

# --- Rutas de Análisis ---

@router.post("/analyze/pdf")
async def analyze_pdf_endpoint(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    session_handler: SessionHandler = Depends(get_session_handler)
):
    # NOTA: La validación de tipo de archivo ya se hace en main.py y en el ML-Core, pero aquí se previene el fallo.
    if file.content_type not in settings.SUPPORTED_PDF_EXTENSIONS:
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")
    
    # Aquí se podría poner lógica adicional del Backend si fuera necesario antes de llamar al ML.
    # Por ejemplo, autenticación o logging.
    
    result = await summarizer_service.analyze_pdf_request(file, session_id)
    return result

@router.post("/analyze/video")
async def analyze_video_endpoint(request_data: Dict[str, Any]):
    url = request_data.get("url")
    session_id = request_data.get("session_id")
    
    if not url or not session_id:
        raise HTTPException(status_code=400, detail="Faltan URL o ID de sesión.")
        
    if not any(platform in url for platform in settings.SUPPORTED_VIDEO_PLATFORMS):
        raise HTTPException(status_code=400, detail="Plataforma de video no soportada.")
        
    result = await summarizer_service.analyze_video_request(url, session_id)
    return result

@router.post("/generate/quiz/{document_id}")
async def generate_quiz_endpoint(document_id: int):
    result = await summarizer_service.generate_quiz_request(document_id)
    return result

# --- Rutas de Historial (Usan la BD/Cache directamente) ---

@router.get("/session/{session_id}/history")
async def get_history_endpoint(
    session_id: str, 
    session_handler: SessionHandler = Depends(get_session_handler)
):
    """Obtiene el historial de documentos procesados para una sesión."""
    try:
        # Se asume que get_session_handler devuelve un SessionHandler
        # que ya tiene acceso a la DB y Cache.
        history = session_handler.get_session_history(session_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {e}")