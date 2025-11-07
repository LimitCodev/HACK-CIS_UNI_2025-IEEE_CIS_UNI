from typing import Dict, Any, Optional

class ModelConfig:
    """
    Define los parámetros de inferencia y la lógica de decisión de los modelos.
    """
    
    # Parámetros de inferencia por defecto (Temperatura para creatividad controlada)
    DEFAULT_PARAMS: Dict[str, Any] = {
        "temperature": 0.3,
        "max_tokens": 4096,
        "top_p": 1.0
    }
    
    # Mapeo de modelos a sus características (para uso futuro)
    MODEL_MAP: Dict[str, Dict[str, Any]] = {
        "gpt-4o": {"client": "openai", "context_window": 128000, "cost_priority": 1},
        "gpt-4o-mini": {"client": "openai", "context_window": 128000, "cost_priority": 2},
        "claude-3-5-sonnet": {"client": "anthropic", "context_window": 200000, "cost_priority": 1},
        # Añadiría 'llama3-8b' aquí si usas Ollama/local
    }

    @classmethod
    def get_inference_params(cls, model_name: str) -> Dict[str, Any]:
        """Obtiene los parámetros de inferencia para un modelo específico."""
        
        # Puedes añadir lógica aquí para ajustar la temperatura si es un quiz vs. resumen.
        if "quiz" in model_name:
            # Para tareas de precisión (quiz, validación), bajamos la temperatura
            return {**cls.DEFAULT_PARAMS, "temperature": 0.1}
        
        return cls.DEFAULT_PARAMS