# Contenido de /ml-core/prompts/__init__.py

from .pdf_prompts import (
    SYSTEM_PROMPT_SUMMARIZER,
    get_pdf_summary_prompt,
    get_chunk_summary_prompt,
    get_combine_summaries_prompt,
    get_metadata_extraction_prompt
)

from .video_prompts import (
    SYSTEM_PROMPT_VIDEO_SUMMARIZER,
    get_video_summary_prompt,
    get_video_chunk_summary_prompt,
    get_combine_video_summaries_prompt
)

from .quiz_prompts import (
    SYSTEM_PROMPT_QUIZ_GENERATOR,
    get_quiz_for_video_prompt,
    get_quiz_for_pdf_prompt,
    get_quiz_validation_prompt
)

__all__ = [
    "SYSTEM_PROMPT_SUMMARIZER",
    "get_pdf_summary_prompt",
    "get_chunk_summary_prompt",
    "get_combine_summaries_prompt",
    "get_metadata_extraction_prompt",

    "SYSTEM_PROMPT_VIDEO_SUMMARIZER",
    "get_video_summary_prompt",
    "get_video_chunk_summary_prompt",
    "get_combine_video_summaries_prompt",

    "SYSTEM_PROMPT_QUIZ_GENERATOR",
    "get_quiz_for_video_prompt",
    "get_quiz_for_pdf_prompt",
    "get_quiz_validation_prompt"
]