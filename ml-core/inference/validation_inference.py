from typing import Dict, Any

class ValidationInference:
    """
    Clase dedicada a ejecutar inferencia para tareas de evaluación de calidad,
    como la validación de quizzes generados por la IA.
    """
    def __init__(self, run_model_func):
        """
        Inicializa con la función de ejecución de modelo (AIService._run_model) 
        para mantener la separación de responsabilidades.
        """
        self._run_model = run_model_func

    async def validate_quiz_quality(self, quiz_data: Dict[str, Any], get_validation_prompt_func) -> Dict[str, Any]:
        """
        Ejecuta el pipeline de validación para un cuestionario generado.
        
        Args:
            quiz_data: El diccionario del cuestionario generado por la IA.
            get_validation_prompt_func: La función que obtiene el prompt de /prompts/quiz_prompts.py.
            
        Returns:
            Un diccionario JSON con los puntajes y feedback de la validación.
        """
        print("    -> Iniciando proceso de validación del Quiz...")
        
        # 1. Obtener el prompt especializado
        validation_prompt = get_validation_prompt_func(quiz_data)
        
        # 2. Ejecutar el LLM para evaluar la respuesta anterior
        # Se asume que _run_model es una función asíncrona
        try:
            validation_result = await self._run_model(
                prompt=validation_prompt, 
                response_format="json", 
                # Podrías usar un modelo más pequeño aquí para ahorrar costos, 
                # ya que solo está evaluando un JSON pequeño.
                model="gpt-4o-mini" 
            )
            print(f"    -> Validación obtenida. Puntaje: {validation_result.get('overall_score', 'N/A')}")
            return validation_result
            
        except Exception as e:
            print(f"    ERROR: Falló la inferencia de validación: {e}")
            # Devolvemos un resultado de error en caso de fallo de API
            return {"error": "Validación de IA fallida", "overall_score": 0.0}