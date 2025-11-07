SYSTEM_PROMPT_QUIZ_GENERATOR = """Eres un experto pedagogo y diseñador de evaluaciones educativas.
Tu especialidad es crear preguntas de opción múltiple que evalúen comprensión profunda,
no solo memorización. Tus preguntas son claras, desafiantes y justas."""


def get_quiz_for_pdf_prompt(summary: dict, num_questions: int = 5) -> dict:
    user_prompt = f"""Genera un quiz de {num_questions} preguntas sobre el siguiente documento:

**RESUMEN DEL DOCUMENTO:**
- {summary.get('summary_medium', '')}
- **Conceptos clave**: {', '.join(summary.get('key_concepts', []))}
- **Tipo de documento**: {summary.get('document_type', 'academic')}

---

**INSTRUCCIONES:**

**DISTRIBUCIÓN DE PREGUNTAS:**
- {num_questions // 2} preguntas de comprensión conceptual
- {num_questions - (num_questions // 2)} preguntas de aplicación/análisis

**REGLAS ESTRICTAS:**

1. **Estructura de cada pregunta:**
   - Pregunta clara y específica
   - 4 opciones (A, B, C, D)
   - Solo UNA respuesta correcta
   - Explicación breve de por qué es correcta

2. **Calidad de las opciones:**
   - Longitud similar entre todas las opciones
   - Sin pistas sintácticas
   - Distractores plausibles
   - Evita opciones absurdas

3. **Tipos de preguntas a incluir:**
   - Definiciones y conceptos clave
   - Relaciones causa-efecto
   - Aplicación de conceptos
   - Comparaciones entre conceptos

**FORMATO DE RESPUESTA (JSON):**
```json
{{
  "quiz_title": "Quiz sobre [Tema del material]",
  "difficulty": "medium",
  "estimated_time": 10,
  "questions": [
    {{
      "question_number": 1,
      "question_text": "¿Cuál de las siguientes afirmaciones describe mejor el concepto de X?",
      "question_type": "conceptual",
      "options": [
        {{"id": "A", "text": "Opción A plausible pero incorrecta"}},
        {{"id": "B", "text": "Opción correcta con descripción precisa"}},
        {{"id": "C", "text": "Opción C distractor común"}},
        {{"id": "D", "text": "Opción D otra variante plausible"}}
      ],
      "correct_answer": "B",
      "explanation": "La opción B es correcta porque...",
      "related_concepts": ["concepto1", "concepto2"]
    }}
  ],
  "learning_objectives_covered": [
    "Comprender el concepto X",
    "Aplicar el principio Y"
  ]
}}
```"""

    return {
        "system": SYSTEM_PROMPT_QUIZ_GENERATOR,
        "user": user_prompt
    }


def get_quiz_for_video_prompt(summary: dict, num_questions: int = 5) -> dict:
    user_prompt = f"""Genera un quiz de {num_questions} preguntas sobre el siguiente video:

**RESUMEN DEL VIDEO:**
- {summary.get('summary_medium', '')}
- **Conceptos clave**: {', '.join(summary.get('key_concepts', []))}
- **Tipo de video**: {summary.get('video_type', 'educational')}
- **Puntos clave**: {summary.get('main_takeaways', [])}

---

**INSTRUCCIONES ESPECIALES PARA VIDEOS:**

1. Enfócate en los **main takeaways** (puntos clave para recordar)
2. Si el video es tutorial/código:
   - Incluye preguntas sobre implementación
   - Pregunta sobre errores comunes mencionados
   - Evalúa comprensión de conceptos, no memorización

3. **Tipos de preguntas recomendadas:**
   - "¿Qué se demostró en la sección X?"
   - "¿Por qué el instructor recomendó usar Y en lugar de Z?"
   - "¿Qué error común se mencionó respecto a...?"

**FORMATO:** Usar el mismo JSON que el prompt de PDF.

**EVITAR:**
- Preguntas sobre timestamps específicos
- Preguntas sobre detalles visuales que no están en la transcripción
- Trivialidades sobre el orden exacto de los temas"""

    return {
        "system": SYSTEM_PROMPT_QUIZ_GENERATOR,
        "user": user_prompt
    }
# --- PROMPT CRÍTICO PARA INNOVACIÓN (VALIDACIÓN DE CALIDAD) ---

def get_quiz_validation_prompt(quiz_data: dict) -> dict:
    """
    Prompt para que un LLM evalúe la calidad y coherencia de otro LLM.
    """
    import json
    quiz_str = json.dumps(quiz_data, indent=2)
    
    user_prompt = f"""Eres un experto pedagogo y revisor de contenido. 
    Tu tarea es evaluar el siguiente cuestionario generado por IA en base a su coherencia, dificultad y relevancia académica.

    **CUESTIONARIO A EVALUAR:**
    {quiz_str}

    ---
    
    **CRITERIOS DE EVALUACIÓN (Escala 0-10):**
    1. Relevancia: ¿Las preguntas se basan directamente en el contenido resumido?
    2. Coherencia: ¿Las opciones de respuesta son lógicas y gramaticalmente correctas?
    3. Dificultad: ¿La dificultad se ajusta al nivel "medium" o al nivel solicitado?
    4. Fidelidad: ¿Las explicaciones son fieles a la respuesta correcta y al tema central?

    **FORMATO DE RESPUESTA (JSON):**
    ```json
    {{
      "relevance_score": 9,
      "coherence_score": 8,
      "difficulty_score": 7,
      "fidelity_score": 9,
      "overall_score": 8.5,
      "feedback": "El cuestionario es sólido. Sugiero variar el tipo de pregunta.",
      "validation_score": 8.5
    }}
    ```
    """
    return {
        "system": "Eres un evaluador experto de evaluaciones académicas.",
        "user": user_prompt
    }
    
# --- Funciones de Generación (Necesarias para el init que enviaste) ---
# NOTA: Aunque no se usan en el llm_service.py, el __init__.py las importa.

def get_quiz_generation_prompt(summary: dict, num_questions: int = 5) -> dict:
    # Placeholder para la función principal de generación
    return get_quiz_for_pdf_prompt(summary, num_questions)

def get_regenerate_question_prompt(question: dict, feedback: str) -> dict:
    # Placeholder para la regeneración de preguntas fallidas
    pass