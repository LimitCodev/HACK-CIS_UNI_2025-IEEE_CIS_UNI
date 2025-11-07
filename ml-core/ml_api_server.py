import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel, Field
from pathlib import Path
import os
import shutil

# Importa las configuraciones y el servicio principal de IA
from config import settings
from llm_service import AIService 

# --- 1. MODELOS DE DATOS (Pydantic para validación de entrada/salida) ---

class BaseResponse(BaseModel):
    """Modelo base para respuestas estandarizadas."""
    status: str = "success"
    message: str

class AnalysisRequest(BaseModel):
    """Modelo para la solicitud de análisis de URL."""
    session_id: str = Field(..., description="ID único de la sesión del usuario.")
    url: str = Field(..., description="URL del video de YouTube a analizar.")

class AnalysisResponse(BaseResponse):
    """Modelo para la respuesta después del análisis."""
    document_id: int
    title: str
    summary_short: str
    cached: bool = False

class QuizResponse(BaseResponse):
    """Modelo para la respuesta de generación de Quiz."""
    quiz_id: int
    validation_score: float = Field(..., description="Puntaje de validación de calidad del quiz (0.0 a 1.0).")
    quiz_data: dict
    
# --- 2. INICIALIZACIÓN DE FASTAPI Y SERVICIO ---

app = FastAPI(
    title=settings.PROJECT_NAME + " - ML Service",
    version=settings.VERSION,
    description="Microservicio dedicado a la generación de contenido (resúmenes, quizzes) usando LLMs."
)

# Inicializa el servicio de IA globalmente, manejando dependencias.
try:
    # La clase AIService ya contiene la lógica de DB, Cache, Prompts, etc.
    ai_service = AIService()
    print("✅ AIService inicializado correctamente.")
except Exception as e:
    print(f"❌ ERROR CRÍTICO al inicializar AIService: {e}")
    # Esto forzará el fallo del contenedor si no puede iniciar la DB/Cache.
    raise RuntimeError("Fallo en la inicialización de dependencias del servicio ML.")


# --- 3. FUNCIONES AUXILIARES ---

def _save_upload_file(upload_file: UploadFile, session_id: str) -> Path:
    """Guarda el archivo subido en la carpeta de uploads."""
    
    # Crea el directorio si no existe (usado en contenedores Docker)
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    
    # Usa el session_id para crear una ruta de archivo única
    # Esto es crucial para que el backend pueda encontrar el archivo luego.
    safe_filename = f"{session_id}_{upload_file.filename}"
    file_path = settings.UPLOADS_DIR / safe_filename
    
    try:
        with open(file_path, "wb") as buffer:
            # Escribe el contenido del archivo subido en el disco
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        # Limpieza en caso de error de escritura
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {e}")

    return file_path


# --- 4. ENDPOINTS ---

@app.get("/health", response_model=BaseResponse)
async def health_check():
    """Endpoint de verificación de salud."""
    # Opcionalmente, puedes añadir aquí checks de conexión a DB/Cache.
    return BaseResponse(status="success", message="ML Service is running and healthy.")

@app.post("/analyze/pdf", response_model=AnalysisResponse)
async def analyze_pdf(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Procesa un PDF subido, extrae texto, lo resume y lo guarda.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")
        
    try:
        file_path = _save_upload_file(file, session_id)
        
        # Llama a tu lógica principal de IA
        result = await ai_service.analyze_pdf(
            file_path=str(file_path),
            session_id=session_id,
            filename=file.filename
        )
        
        # Elimina el archivo local después de procesar
        os.remove(file_path)

        return AnalysisResponse(
            message="PDF analizado y resumido correctamente.",
            document_id=result.get("document_id"),
            title=result.get("title"),
            summary_short=result.get("summary_short"),
            cached=result.get("cached", False)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error en analyze_pdf: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el PDF.")

@app.post("/analyze/video", response_model=AnalysisResponse)
async def analyze_video(request: AnalysisRequest):
    """
    Analiza un video de YouTube, lo transcribe, resume y lo guarda.
    """
    try:
        # Llama a tu lógica principal de IA
        result = await ai_service.analyze_video(
            youtube_url=request.url,
            session_id=request.session_id
        )

        return AnalysisResponse(
            message="Video de YouTube transcrito y resumido correctamente.",
            document_id=result.get("document_id"),
            title=result.get("title"),
            summary_short=result.get("summary_short"),
            cached=result.get("cached", False)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error en analyze_video: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el video.")


@app.post("/generate/quiz/{document_id}", response_model=QuizResponse)
async def generate_quiz_endpoint(document_id: int):
    """
    Genera un quiz de dificultad media basado en un documento ya analizado.
    """
    try:
        # Llama a tu lógica principal de IA
        result = await ai_service.generate_quiz(
            document_id=document_id,
            difficulty="medium" # Puedes parametrizar esto
        )

        return QuizResponse(
            message="Quiz generado y validado con éxito.",
            quiz_id=result.get("quiz_id"),
            validation_score=result.get("validation_score"),
            quiz_data=result.get("quiz_data")
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error en generate_quiz: {e}")
        raise HTTPException(status_code=500, detail="Error interno al generar el quiz.")