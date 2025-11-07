from openai import OpenAI
from typing import List, Dict
import numpy as np

class EmbeddingsGenerator:
    """
    Genera embeddings de vectores para el texto, esencial para RAG y búsqueda semántica.
    """
    def __init__(self, settings):
        # Usamos el cliente de OpenAI/API para generar embeddings
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"
        self.settings = settings

    def generate_embedding(self, text: str) -> List[float]:
        """Convierte un texto simple en un vector de alta dimensión."""
        if not self.settings.OPENAI_API_KEY:
            # Fallback si no hay clave: devuelve un vector vacío
            return [0.0] * 1536 

        try:
            response = self.openai_client.embeddings.create(
                input=[text],
                model=self.embedding_model
            )
            # Retorna el primer vector
            return response.data[0].embedding
        except Exception as e:
            print(f"ERROR: Falló la generación de embeddings: {e}")
            return [0.0] * 1536
    
    # Opcional: Función para encontrar documentos similares (para RAG)
    def find_similar_chunks(self, query_vector: List[float], all_vectors: List[Dict]):
        """
        Busca los vectores más cercanos a una consulta (simulación de Vector DB).
        """
        # Aquí iría la lógica para usar un Vector DB real como ChromaDB o FAISS,
        # pero para el hackathon, es un placeholder.
        pass