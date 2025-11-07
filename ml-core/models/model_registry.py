from typing import Literal

class ModelRegistry:
    """
    Registra los modelos disponibles y devuelve el cliente de API asociado.
    """
    
    def __init__(self, settings):
        self.settings = settings

    def get_client_for_model(self, model_name: str) -> Literal['openai', 'anthropic', 'unsupported']:
        """
        Determina qué cliente de API (OpenAI o Anthropic) manejará la inferencia.
        """
        # Utiliza la información del mapeo de ModelConfig
        from .model_config import ModelConfig 
        model_info = ModelConfig.MODEL_MAP.get(model_name)
        
        if model_info:
            return model_info.get("client", "unsupported")
        
        # Lógica de fallback para modelos no mapeados
        if "gpt" in model_name.lower():
            return "openai"
        if "claude" in model_name.lower():
            return "anthropic"
        
        return "unsupported"