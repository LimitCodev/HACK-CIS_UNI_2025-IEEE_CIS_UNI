import redis
import json
from typing import Any, Optional
from config import settings


class CacheManager:
    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        try:
            self.redis.ping()
            print("Conexión a Redis exitosa.")
        except redis.ConnectionError as e:
            print(f"Error al conectar con Redis: {e}")
            raise
    
    def cache_summary(self, doc_hash: str, summary: dict, ttl: int = 3600) -> bool:
        try:
            key = f"summary:{doc_hash}"
            self.redis.setex(key, ttl, json.dumps(summary))
            return True
        except Exception as e:
            print(f"Error al cachear resumen: {e}")
            return False
    
    def get_cached_summary(self, doc_hash: str) -> Optional[dict]:
        try:
            key = f"summary:{doc_hash}"
            cached = self.redis.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            print(f"Error al obtener resumen cacheado: {e}")
            return None
    
    def cache_quiz(self, doc_id: int, quiz: dict, ttl: int = 1800) -> bool:
        try:
            key = f"quiz:{doc_id}"
            self.redis.setex(key, ttl, json.dumps(quiz))
            return True
        except Exception as e:
            print(f"Error al cachear quiz: {e}")
            return False
    
    def get_cached_quiz(self, doc_id: int) -> Optional[dict]:
        try:
            key = f"quiz:{doc_id}"
            cached = self.redis.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            print(f"Error al obtener quiz cacheado: {e}")
            return None
    
    def invalidate_session_cache(self, session_id: str) -> bool:
        try:
            key = f"history:{session_id}"
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Error al invalidar cache de sesión: {e}")
            return False
    
    def cache_history(self, session_id: str, history: list, ttl: int = 300) -> bool:
        try:
            key = f"history:{session_id}"
            self.redis.setex(key, ttl, json.dumps(history))
            return True
        except Exception as e:
            print(f"Error al cachear historial: {e}")
            return False
    
    def get_cached_history(self, session_id: str) -> Optional[list]:
        try:
            key = f"history:{session_id}"
            cached = self.redis.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            print(f"Error al obtener historial cacheado: {e}")
            return None