import json
import hashlib
import tiktoken
from typing import Optional, Literal
from openai import OpenAI
from anthropic import Anthropic

from prompts.pdf_prompts import (
    get_pdf_summary_prompt,
    get_chunk_summary_prompt,
    get_combine_summaries_prompt,
    get_metadata_extraction_prompt
)
from prompts.video_prompts import (
    get_video_summary_prompt,
    get_video_chunk_summary_prompt,
    get_combine_video_summaries_prompt
)
from prompts.quiz_prompts import (
    get_quiz_for_video_prompt,
    get_quiz_for_pdf_prompt,
    get_quiz_validation_prompt  # Importación añadida
)

from processing.pdf_processor import PDFProcessor
from processing.video_processor import VideoProcessor
from processing.text_chunker import TextChunker

from database.db_manager import DatabaseManager
from database.cache_manager import CacheManager
from database.session_handler import SessionHandler
from database.models import Document, Quiz

from config import settings


def count_tokens(text: str, model_name: str = "gpt-4") -> int:
    model_encoding_map = {
        "gpt-4": "cl100k_base",
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "claude-3-5-sonnet": "cl100k_base",
    }
    
    try:
        encoding_name = model_encoding_map.get(model_name, "cl100k_base")
        encoding = tiktoken.get_encoding(encoding_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    return len(encoding.encode(text))


class AIService:
    def __init__(self):
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        self.pdf_handler = PDFProcessor()
        self.video_handler = VideoProcessor()
        self.text_chunker = TextChunker()

        self.db = DatabaseManager()
        self.cache = CacheManager()
        self.sessions = SessionHandler(
            db=self.db.get_session(),
            redis_client=self.cache.redis
        )

        self.default_model = settings.DEFAULT_LLM_MODEL
        self.max_chunk_size = settings.MAX_CHUNK_SIZE


    async def analyze_pdf(self, file_path: str, session_id: str, filename: str = "document.pdf") -> dict:
        try:
            print(f"Extrayendo texto de {filename}...")
            extracted_text = self.pdf_handler.extract_text(file_path)

            if not extracted_text or len(extracted_text) < 100:
                return {"error": "El PDF no contiene suficiente texto."}

            content_hash = hashlib.sha256(extracted_text.encode()).hexdigest()

            print("Verificando duplicados...")
            existing_doc = self.sessions.check_duplicate(extracted_text, session_id)
            if existing_doc:
                print("Documento encontrado en la base de datos.")
                return {
                    "document_id": existing_doc.id,
                    "title": existing_doc.title,
                    "summary_short": existing_doc.summary_short,
                    "summary_medium": existing_doc.summary_medium,
                    "summary_long": json.loads(existing_doc.summary_long),
                    "key_concepts": existing_doc.metadata.get("key_concepts", []),
                    "cached": True
                }

            cached_summary = self.cache.get_cached_summary(content_hash)
            if cached_summary:
                print("Resumen encontrado en caché.")
                doc = self._save_document(
                    session_id=session_id,
                    doc_type="pdf",
                    title=filename,
                    content_hash=content_hash,
                    raw_content=extracted_text,
                    summary=cached_summary
                )
                return {**cached_summary, "document_id": doc.id, "cached": True}

            print("Contando tokens...")
            token_count = count_tokens(extracted_text, self.default_model)
            print(f"Total de tokens: {token_count}")

            print("Generando resumen con modelo...")
            if token_count > self.max_chunk_size:
                summary = await self._long_doc_summary(extracted_text, filename, token_count)
            else:
                summary = await self._short_doc_summary(extracted_text, filename)

            self.cache.cache_summary(content_hash, summary, ttl=3600)

            doc = self._save_document(
                session_id=session_id,
                doc_type="pdf",
                title=summary.get("title", filename),
                content_hash=content_hash,
                raw_content=extracted_text,
                summary=summary
            )

            print(f"PDF procesado correctamente (ID: {doc.id})")
            return {**summary, "document_id": doc.id, "cached": False}

        except Exception as e:
            print(f"Error al procesar PDF: {e}")
            return {"error": str(e)}


    async def analyze_video(self, youtube_url: str, session_id: str) -> dict:
        try:
            print("Obteniendo información del video...")
            video_info = self.video_handler.get_video_info(youtube_url)

            db_session = self.db.get_session()
            existing_doc = db_session.query(Document).filter(
                Document.session_id == session_id,
                Document.source_url == youtube_url
            ).first()

            if existing_doc:
                print("Video ya procesado anteriormente.")
                return {
                    "document_id": existing_doc.id,
                    "title": existing_doc.title,
                    "summary_short": existing_doc.summary_short,
                    "summary_medium": existing_doc.summary_medium,
                    "summary_long": json.loads(existing_doc.summary_long),
                    "video_url": youtube_url,
                    "duration": existing_doc.metadata.get("duration"),
                    "cached": True
                }

            print("Transcribiendo audio...")
            try:
                transcript = await self.video_handler.transcribe_video(youtube_url)
            except Exception as transcribe_error:
                return {"error": f"Error al transcribir video: {str(transcribe_error)}"}

            if not transcript or len(transcript) < 100:
                return {"error": "No se pudo obtener una transcripción válida del video."}

            content_hash = hashlib.sha256(transcript.encode()).hexdigest()
            cached_summary = self.cache.get_cached_summary(content_hash)

            if cached_summary:
                print("Resumen de transcripción encontrado en caché.")
                doc = self._save_document(
                    session_id=session_id,
                    doc_type="video",
                    title=video_info["title"],
                    content_hash=content_hash,
                    raw_content=transcript,
                    summary=cached_summary,
                    source_url=youtube_url,
                    metadata={"duration": video_info.get("duration")}
                )
                return {**cached_summary, "document_id": doc.id, "cached": True}

            print("Contando tokens...")
            token_count = count_tokens(transcript, self.default_model)
            print(f"Total de tokens: {token_count}")

            print("Generando resumen del video...")
            if token_count > self.max_chunk_size:
                summary = await self._long_video_summary(transcript, video_info["title"], video_info.get("duration"), token_count)
            else:
                summary = await self._short_video_summary(transcript, video_info["title"], video_info.get("duration"))

            self.cache.cache_summary(content_hash, summary, ttl=3600)

            doc = self._save_document(
                session_id=session_id,
                doc_type="video",
                title=summary.get("title", video_info["title"]),
                content_hash=content_hash,
                raw_content=transcript,
                summary=summary,
                source_url=youtube_url,
                metadata={
                    "duration": video_info.get("duration"),
                    "channel": video_info.get("channel")
                }
            )

            print(f"Video procesado correctamente (ID: {doc.id})")
            return {
                **summary,
                "document_id": doc.id,
                "video_url": youtube_url,
                "duration": video_info.get("duration"),
                "cached": False
            }

        except Exception as e:
            print(f"Error al procesar video: {e}")
            return {"error": str(e)}


    async def generate_quiz(self, document_id: int, num_questions: int = 5, difficulty: Literal["easy", "medium", "hard"] = "medium") -> dict:
        try:
            db_session = self.db.get_session()
            document = db_session.query(Document).get(document_id)

            if not document:
                return {"error": f"Documento {document_id} no encontrado."}

            cached_quiz = self.cache.get_cached_quiz(document_id)
            if cached_quiz:
                print("Quiz encontrado en caché.")
                return cached_quiz

            summary = {
                "summary_short": document.summary_short,
                "summary_medium": document.summary_medium,
                "summary_long": json.loads(document.summary_long),
                "key_concepts": document.metadata.get("key_concepts", []),
                "document_type": document.metadata.get("document_type", "general")
            }

            print(f"Generando quiz ({difficulty}, {num_questions} preguntas)...")

            if document.doc_type == "video":
                prompt = get_quiz_for_video_prompt(summary, num_questions)
            else:
                prompt = get_quiz_for_pdf_prompt(summary, num_questions)

            quiz_data = await self._run_model(prompt, response_format="json")

            # Lógica de validación de calidad
            validation_prompt = get_quiz_validation_prompt(quiz_data)
            validation = await self._run_model(validation_prompt, response_format="json")
            validation_score = validation.get("validation_score", 0)

            quiz = Quiz(
                document_id=document_id,
                questions=quiz_data["questions"],
                difficulty=difficulty,
                metadata={
                    "num_questions": num_questions,
                    "validation_score": validation_score  # Guardar validation_score en metadata
                }
            )
            db_session.add(quiz)
            db_session.commit()

            result = {
                "quiz_id": quiz.id,
                "document_id": document_id,
                **quiz_data
            }
            self.cache.cache_quiz(document_id, result, ttl=1800)

            print(f"Quiz generado correctamente (ID: {quiz.id})")
            return result

        except Exception as e:
            print(f"Error al generar quiz: {e}")
            return {"error": str(e)}


    async def _short_doc_summary(self, content: str, title: str) -> dict:
        metadata_prompt = get_metadata_extraction_prompt(content)
        metadata = await self._run_model(metadata_prompt, response_format="json")

        prompt = get_pdf_summary_prompt(content, title)
        summary = await self._run_model(prompt, response_format="json")

        summary["metadata"] = metadata
        return summary


    async def _long_doc_summary(self, content: str, title: str, token_count: int) -> dict:
        metadata_prompt = get_metadata_extraction_prompt(content)
        metadata = await self._run_model(metadata_prompt, response_format="json")

        chunks = self.text_chunker.chunk_text(content, max_size=self.max_chunk_size)
        print(f"Documento dividido en {len(chunks)} partes.")

        
        chunk_summaries = [
            await self._run_model(get_chunk_summary_prompt(chunk, i, len(chunks)))
            for i, chunk in enumerate(chunks)
        ]
        print(f"Todas las {len(chunks)} partes han sido resumidas.")


        combine_prompt = get_combine_summaries_prompt(chunk_summaries, title)
        final_summary = await self._run_model(combine_prompt, response_format="json")

        final_summary.setdefault("document_type", metadata.get("document_type", "other"))
        final_summary.setdefault("estimated_reading_time", max(1, len(content.split()) // 200))
        final_summary["metadata"] = metadata

        return final_summary


    async def _short_video_summary(self, transcript: str, title: str, duration: int = None) -> dict:
        prompt = get_video_summary_prompt(transcript, title, duration)
        return await self._run_model(prompt, response_format="json")


    async def _long_video_summary(self, transcript: str, title: str, duration: int = None, token_count: int = 0) -> dict:
        chunks = self.text_chunker.chunk_text(transcript, max_size=self.max_chunk_size)
        print(f"Transcripción dividida en {len(chunks)} segmentos.")

        
        chunk_summaries = [
            await self._run_model(get_video_chunk_summary_prompt(chunk, i, len(chunks), title))
            for i, chunk in enumerate(chunks)
        ]
        
        print(f"Todos los {len(chunks)} segmentos han sido resumidos.")


        combine_prompt = get_combine_video_summaries_prompt(chunk_summaries, title)
        final_summary = await self._run_model(combine_prompt, response_format="json")

        if duration and not final_summary.get("estimated_watch_time"):
            final_summary["estimated_watch_time"] = duration // 60

        return final_summary


    async def _run_model(self, prompt: dict, response_format: str = "text", model: Optional[str] = None) -> dict | str:
        model = model or self.default_model
        
        try:
            if "gpt" in model:
                messages = [
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ]
                
                if response_format == "json":
                    response = self.openai.chat.completions.create(
                        model=model,
                        messages=messages,
                        response_format={"type": "json_object"},
                        temperature=0.3
                    )
                else:
                    response = self.openai.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.3
                    )
                
                content = response.choices[0].message.content
                return json.loads(content) if response_format == "json" else content

            elif "claude" in model:
                response = self.anthropic.messages.create(
                    model=model,
                    max_tokens=4096,
                    system=prompt["system"],
                    messages=[{"role": "user", "content": prompt["user"]}],
                    temperature=0.3
                )
                
                content = response.content[0].text
                return json.loads(content) if response_format == "json" else content

            else:
                raise ValueError(f"Modelo no soportado: {model}")

        except Exception as e:
            print(f"Error al ejecutar modelo: {e}")
            raise


    def _save_document(self, session_id: str, doc_type: str, title: str, content_hash: str,
                        raw_content: str, summary: dict, source_url: str = None, metadata: dict = None) -> Document:
        db_session = self.db.get_session()

        doc = Document(
            session_id=session_id,
            doc_type=doc_type,
            title=title,
            source_url=source_url,
            content_hash=content_hash,
            summary_short=summary.get("summary_short"),
            summary_medium=summary.get("summary_medium"),
            summary_long=json.dumps(summary.get("summary_long", [])),
            raw_content=raw_content,
            metadata={
                **(metadata or {}),
                "key_concepts": summary.get("key_concepts", []),
                "document_type": summary.get("document_type"),
                "estimated_reading_time": summary.get("estimated_reading_time"),
                **summary.get("metadata", {})
            }
        )

        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)
        self.cache.invalidate_session_cache(session_id)
        
        return doc