from .model_config import ModelConfig
from typing import Optional, Literal

class FallbackLogic:
    """
    Implementa la lógica para seleccionar un modelo alternativo (fallback) 
    cuando el modelo principal falla o excede el límite de tokens.
    """
    
    def __init__(self, settings):
        self.settings = settings

    def get_fallback_model(self, failed_model: str) -> str:
        """
        Selecciona un modelo de fallback, priorizando el ahorro y la disponibilidad.
        """
        
        # Lógica de ejemplo: si GPT-4o falla, caemos a GPT-4o-mini (más barato)
        if failed_model == self.settings.DEFAULT_LLM_MODEL:
            print(f"⚠️ Fallo en modelo primario ({failed_model}). Usando fallback: {self.settings.FALLBACK_LLM_MODEL}")
            return self.settings.FALLBACK_LLM_MODEL
        
        # Si el fallback también falla, intentamos con el otro proveedor (Claude)
        if "gpt" in failed_model.lower():
            print("⚠️ Fallo en fallback de OpenAI. Intentando con Claude.")
            # Esto asume que tienes un modelo Claude de respaldo
            return "claude-3-5-sonnet"
        
        # Último recurso: error fatal
        raise ConnectionError(f"Todos los modelos LLM han fallado, incluyendo el fallback.")