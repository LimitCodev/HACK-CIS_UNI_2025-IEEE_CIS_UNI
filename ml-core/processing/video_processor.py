import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from openai import OpenAI
from config import settings
import tempfile
import os
import asyncio

class VideoProcessor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    def get_video_info(self, youtube_url: str) -> dict:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                return {
                    "title": info.get("title", "Video sin título"),
                    "duration": info.get("duration", 0),
                    "channel": info.get("uploader", "Desconocido"),
                    "video_id": info.get("id", "")
                }
        except Exception as e:
            raise ValueError(f"Error al obtener información del video: {str(e)}")
    
    async def transcribe_video(self, youtube_url: str) -> str:
        video_info = self.get_video_info(youtube_url)
        video_id = video_info.get("video_id")
        
        if not video_id:
            raise ValueError("No se pudo extraer el ID del video")
        
        transcript_text = self._try_youtube_transcripts(video_id)
        
        if transcript_text:
            return transcript_text
        
        print("No hay subtítulos disponibles. Intentando transcribir con Whisper...")
        return await self._transcribe_with_whisper(youtube_url)
    
    def _try_youtube_transcripts(self, video_id: str) -> str | None:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            try:
                transcript = transcript_list.find_transcript(['es', 'es-ES'])
            except NoTranscriptFound:
                try:
                    transcript = transcript_list.find_transcript(['en', 'en-US'])
                except NoTranscriptFound:
                    transcript = transcript_list.find_generated_transcript(['es', 'en'])
            
            transcript_data = transcript.fetch()
            transcript_text = " ".join([entry['text'] for entry in transcript_data])
            
            print(f"Transcripción obtenida de YouTube (idioma: {transcript.language_code})")
            return transcript_text
            
        except (TranscriptsDisabled, NoTranscriptFound, Exception) as e:
            print(f"No se pudieron obtener subtítulos de YouTube: {str(e)}")
            return None
    
    async def _transcribe_with_whisper(self, youtube_url: str) -> str:
        if not self.openai_client:
            raise ValueError("API key de OpenAI no configurada para usar Whisper")
        
        temp_audio = None
        try:
            temp_audio = self._download_audio(youtube_url)
            
            print(f"Transcribiendo audio con Whisper...")
            def sync_transcribe(audio_path):
                """Función síncrona que contiene la llamada bloqueante."""
                with open(audio_path, "rb") as audio_file:
                    return self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="es"
                    )
            transcript = await asyncio.to_thread(
                sync_transcribe,
                temp_audio
        )
            return transcript.text
            
        except Exception as e:
            raise ValueError(f"Error al transcribir con Whisper: {str(e)}")
        
        finally:
            if temp_audio and os.path.exists(temp_audio):
                try:
                    os.remove(temp_audio)
                except:
                    pass
    
    def _download_audio(self, youtube_url: str) -> str:
        temp_dir = tempfile.gettempdir()
        temp_audio = os.path.join(temp_dir, "temp_audio.mp3")
        
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": temp_audio.replace(".mp3", ""),
            "quiet": True,
            "no_warnings": True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            return temp_audio
            
        except Exception as e:
            raise ValueError(f"Error al descargar audio: {str(e)}")