import httpx
from fastapi import UploadFile, HTTPException
from typing import Optional, Literal, Dict, Any

from database.db_manager import DatabaseManager
from database.cache_manager import CacheManager
from database.session_handler import SessionHandler
from database.models import Document, Quiz 

from core.config import settings
import uuid
import json
import asyncio


class SummarizerService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.cache_manager = CacheManager()
        self.ml_core_url = settings.ML_CORE_URL 
        self.http_client: Optional[httpx.AsyncClient] = None
        
    async def initialize(self):
        """Inicializa recursos pesados de forma asíncrona."""
        self.http_client = httpx.AsyncClient(base_url=self.ml_core_url, timeout=300.0)

    async def close(self):
        """Cierra recursos al apagar la aplicación."""
        if self.http_client:
            await self.http_client.close()

    async def analyze_pdf_request(
        self,
        file: UploadFile,
        session_id: str
    ) -> Dict[str, Any]:
        
        temp_file_bytes = await file.read()
        files = {'file': (file.filename, temp_file_bytes, file.content_type)}
        data = {'session_id': session_id}
        
        try:
            # Asegura que el cliente httpx exista antes de usarlo
            if not self.http_client:
                 raise RuntimeError("HTTP client no inicializado.")
                 
            response = await self.http_client.post(
                "/analyze/pdf", 
                files=files, 
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("error"):
                raise HTTPException(status_code=400, detail=f"ML Service error: {result['error']}")
            
            return result
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=503, 
                detail=f"Error en el microservicio ML. Respuesta: {e.response.json().get('detail', 'Error desconocido')}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, 
                detail="El Microservicio de Arquitectura ML no está disponible."
            )
        

    async def analyze_video_request(self, youtube_url: str, session_id: str) -> Dict[str, Any]:
        try:
            if not self.http_client:
                 raise RuntimeError("HTTP client no inicializado.")
                 
            response = await self.http_client.post(
                "/analyze/video", 
                json={"url": youtube_url, "session_id": session_id}
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("error"):
                raise HTTPException(status_code=400, detail=f"ML Service error: {result['error']}")
            
            return result
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, 
                detail="El Microservicio de Arquitectura ML no está disponible."
            )

    async def generate_quiz_request(self, document_id: int) -> Dict[str, Any]:
        try:
            if not self.http_client:
                 raise RuntimeError("HTTP client no inicializado.")
                 
            response = await self.http_client.post(f"/generate/quiz/{document_id}")
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("error"):
                raise HTTPException(status_code=400, detail=f"ML Service error: {result['error']}")
            
            return result
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, 
                detail="El Microservicio de Arquitectura ML no está disponible."
            )