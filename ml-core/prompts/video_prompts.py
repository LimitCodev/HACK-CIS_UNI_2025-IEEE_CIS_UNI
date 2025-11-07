SYSTEM_PROMPT_VIDEO_SUMMARIZER = """Eres un asistente experto en análisis de contenido audiovisual educativo y técnico.
Tu especialidad es sintetizar transcripciones de videos (clases, tutoriales, conferencias) 
en resúmenes estructurados que capturen los puntos clave y el flujo narrativo del contenido."""


def get_video_summary_prompt(transcript: str, video_title: str, duration: int = None) -> dict:
    duration_text = f"Duración: {duration // 60} minutos" if duration else ""
    
    user_prompt = f"""Analiza la siguiente transcripción del video "{video_title}" y genera un resumen estructurado.

{duration_text}

**TRANSCRIPCIÓN:**
{transcript}

---

**INSTRUCCIONES:**

1. **RESUMEN CORTO** (2-3 líneas):
   - ¿De qué trata el video?
   - Tipo de contenido: tutorial, clase, conferencia, explicación, etc.

2. **RESUMEN MEDIO** (1 párrafo, 100-150 palabras):
   - Tema principal y subtemas abordados
   - Enfoque pedagógico (si es tutorial: qué se aprende)
   - Público objetivo implícito

3. **RESUMEN LARGO** (Timeline estructurado):
   - Divide el contenido en secciones temáticas
   - Cada sección con: título, descripción breve, conceptos clave
   - Formato: "**[Timestamp] - Tema**: Descripción"

**FORMATO DE RESPUESTA (JSON):**
```json
{{
  "title": "Título del video",
  "summary_short": "Resumen de 2-3 líneas...",
  "summary_medium": "Párrafo descriptivo...",
  "summary_long": [
    "**[00:00-05:30] - Introducción**: Contexto del tema y objetivos del video...",
    "**[05:30-15:00] - Concepto Principal**: Explicación detallada de...",
    "**[15:00-25:00] - Ejemplo Práctico**: Demostración de..."
  ],
  "key_concepts": ["concepto1", "concepto2", "concepto3"],
  "video_type": "tutorial|lecture|explanation|interview|documentary|presentation",
  "difficulty_level": "beginner|intermediate|advanced",
  "prerequisites": ["Conocimiento previo necesario"],
  "main_takeaways": [
    "Punto clave 1 que el espectador debe recordar",
    "Punto clave 2 que el espectador debe recordar"
  ],
  "estimated_watch_time": 25
}}
```

**REGLAS IMPORTANTES:**
- Identifica la estructura pedagógica del video
- Destaca demostraciones prácticas o ejemplos mencionados
- Si el video tiene código, menciona los lenguajes/tecnologías
- Mantén el tono educativo y claro"""

    return {
        "system": SYSTEM_PROMPT_VIDEO_SUMMARIZER,
        "user": user_prompt
    }


def get_video_chunk_summary_prompt(chunk: str, chunk_index: int, total_chunks: int, video_title: str) -> dict:
    user_prompt = f"""Resume el siguiente segmento del video "{video_title}" (parte {chunk_index + 1} de {total_chunks}):

**SEGMENTO DE TRANSCRIPCIÓN:**
{chunk}

---

**TAREA:**
Genera un resumen conciso (4-6 oraciones) que capture:
1. Tema principal del segmento
2. Puntos clave explicados
3. Ejemplos o demostraciones mencionados
4. Transición al siguiente tema (si es evidente)

**FORMATO:**
Un párrafo narrativo que capture el flujo del contenido."""

    return {
        "system": SYSTEM_PROMPT_VIDEO_SUMMARIZER,
        "user": user_prompt
    }


def get_combine_video_summaries_prompt(chunk_summaries: list[str], video_title: str) -> dict:
    combined_text = "\n\n".join([
        f"**Segmento {i+1}:** {summary}" 
        for i, summary in enumerate(chunk_summaries)
    ])
    
    user_prompt = f"""Tienes los resúmenes de diferentes segmentos del video "{video_title}".
Combínalos en un resumen coherente con estructura temporal.

**RESÚMENES DE SEGMENTOS:**
{combined_text}

---

**TAREA:**
Genera el resumen final con los 3 niveles (formato JSON igual que antes).

**ENFOQUE ESPECIAL PARA VIDEOS:**
- En `summary_long`, organiza por timeline/temas
- Identifica el arco narrativo del video
- Destaca cualquier demo o ejemplo práctico mencionado
- En `main_takeaways`, lista 3-5 puntos que alguien debería recordar

```json
{{
  "title": "{video_title}",
  "summary_short": "...",
  "summary_medium": "...",
  "summary_long": [
    "**Introducción (0-5 min)**: Contexto y objetivos...",
    "**Fundamentos (5-15 min)**: Conceptos base explicados..."
  ],
  "key_concepts": [...],
  "video_type": "tutorial",
  "difficulty_level": "intermediate",
  "prerequisites": [...],
  "main_takeaways": [...],
  "estimated_watch_time": 30
}}
```"""

    return {
        "system": SYSTEM_PROMPT_VIDEO_SUMMARIZER,
        "user": user_prompt
    }