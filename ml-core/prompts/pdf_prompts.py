SYSTEM_PROMPT_SUMMARIZER = """Eres un asistente experto en análisis y síntesis de documentos académicos y técnicos. 
Tu especialidad es extraer las ideas principales y presentarlas de forma clara, concisa y estructurada.
Siempre mantienes la fidelidad al contenido original sin agregar información externa."""


def get_pdf_summary_prompt(content: str, doc_title: str = "documento") -> dict:
    user_prompt = f"""Analiza el siguiente documento titulado "{doc_title}" y genera un resumen en 3 niveles:

**DOCUMENTO:**
{content}

---

**INSTRUCCIONES:**

1. **RESUMEN CORTO** (2-3 líneas):
   - Captura la idea principal en máximo 3 oraciones
   - Debe responder: ¿De qué trata este documento?

2. **RESUMEN MEDIO** (1 párrafo, 100-150 palabras):
   - Expande el resumen corto con detalles clave
   - Incluye: objetivo principal, metodología (si aplica), y conclusiones

3. **RESUMEN LARGO** (Bullets estructurados):
   - Organiza por secciones principales del documento
   - Cada bullet debe ser una idea completa (no fragmentos)
   - Máximo 8-10 bullets
   - Formato: "**Sección**: Descripción detallada"

**FORMATO DE RESPUESTA (JSON):**
```json
{{
  "title": "Título extraído del documento",
  "summary_short": "Resumen de 2-3 líneas...",
  "summary_medium": "Párrafo de 100-150 palabras...",
  "summary_long": [
    "**Introducción**: Contexto y problema abordado...",
    "**Metodología**: Enfoque utilizado...",
    "**Resultados**: Hallazgos principales...",
    "**Conclusiones**: Implicaciones y futuras direcciones..."
  ],
  "key_concepts": ["concepto1", "concepto2", "concepto3"],
  "document_type": "paper|presentación|reporte|libro|otro",
  "estimated_reading_time": 15
}}
```

**REGLAS IMPORTANTES:**
- NO inventes información que no esté en el documento
- Usa lenguaje claro y académico
- Mantén objetividad (sin opiniones personales)
- Si el documento tiene fórmulas/ecuaciones clave, menciόnalas
- Extrae 3-5 conceptos clave del documento"""

    return {
        "system": SYSTEM_PROMPT_SUMMARIZER,
        "user": user_prompt
    }


def get_chunk_summary_prompt(chunk: str, chunk_index: int, total_chunks: int) -> dict:
    user_prompt = f"""Resume el siguiente fragmento de documento (parte {chunk_index + 1} de {total_chunks}):

**FRAGMENTO:**
{chunk}

---

**TAREA:**
Genera un resumen conciso (3-5 oraciones) que capture:
1. Ideas principales del fragmento
2. Conceptos clave mencionados
3. Datos o cifras importantes (si hay)

**FORMATO DE RESPUESTA:**
Un párrafo claro y coherente, sin bullets. Enfócate en la esencia del contenido."""

    return {
        "system": SYSTEM_PROMPT_SUMMARIZER,
        "user": user_prompt
    }


def get_combine_summaries_prompt(chunk_summaries: list[str], doc_title: str) -> dict:
    combined_text = "\n\n".join([
        f"**Parte {i+1}:** {summary}" 
        for i, summary in enumerate(chunk_summaries)
    ])
    
    user_prompt = f"""Tienes los resúmenes de las diferentes secciones del documento "{doc_title}".
Tu tarea es combinarlos en un resumen coherente y estructurado.

**RESÚMENES DE SECCIONES:**
{combined_text}

---

**TAREA:**
Genera el resumen final en 3 niveles (JSON igual que antes):

```json
{{
  "title": "{doc_title}",
  "summary_short": "2-3 líneas que capturen la esencia completa...",
  "summary_medium": "Párrafo de 100-150 palabras integrando todas las secciones...",
  "summary_long": [
    "**Sección 1**: Resumen integrado...",
    "**Sección 2**: Resumen integrado..."
  ],
  "key_concepts": ["concepto1", "concepto2"],
  "document_type": "paper|presentación|reporte",
  "estimated_reading_time": 20
}}
```

**REGLAS:**
- Elimina redundancias entre secciones
- Mantén la coherencia narrativa
- Prioriza información más relevante"""

    return {
        "system": SYSTEM_PROMPT_SUMMARIZER,
        "user": user_prompt
    }


def get_metadata_extraction_prompt(content: str) -> dict:
    user_prompt = f"""Analiza el siguiente contenido y extrae metadatos estructurados:

**CONTENIDO:**
{content[:2000]}

---

**TAREA:**
Extrae la siguiente información (si está disponible):

```json
{{
  "title": "Título del documento",
  "authors": ["Autor 1", "Autor 2"],
  "publication_date": "YYYY-MM-DD o null",
  "institution": "Universidad/Organización",
  "document_type": "research_paper|thesis|presentation|report|book_chapter|other",
  "subject_area": "Área temática principal",
  "keywords": ["keyword1", "keyword2"],
  "language": "es|en|other",
  "has_references": true,
  "has_figures": true,
  "has_tables": true
}}
```

**REGLAS:**
- Si algún campo no está disponible, usa `null`
- Infiere el tipo de documento basado en estructura y contenido
- Keywords deben ser conceptos clave del documento (3-7 palabras)"""

    return {
        "system": "Eres un experto en análisis de documentos académicos y extracción de metadatos.",
        "user": user_prompt
    }