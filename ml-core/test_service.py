import asyncio
from llm_service import AIService
from database.db_manager import DatabaseManager
import uuid

async def test_pdf_analysis():
    print("\n=== PROBANDO ANÁLISIS DE PDF ===\n")
    
    service = AIService()
    session_id = str(uuid.uuid4())
    
    pdf_path = "test_document.pdf"
    
    try:
        result = await service.analyze_pdf(
            file_path=pdf_path,
            session_id=session_id,
            filename="Test Document.pdf"
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ PDF procesado correctamente")
            print(f"   ID: {result.get('document_id')}")
            print(f"   Título: {result.get('title')}")
            print(f"   Resumen corto: {result.get('summary_short')[:100]}...")
            print(f"   Cached: {result.get('cached')}")
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


async def test_video_analysis():
    print("\n=== PROBANDO ANÁLISIS DE VIDEO ===\n")
    
    service = AIService()
    session_id = str(uuid.uuid4())
    
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        result = await service.analyze_video(
            youtube_url=youtube_url,
            session_id=session_id
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Video procesado correctamente")
            print(f"   ID: {result.get('document_id')}")
            print(f"   Título: {result.get('title')}")
            print(f"   Duración: {result.get('duration')} segundos")
            print(f"   Resumen corto: {result.get('summary_short')[:100]}...")
            print(f"   Cached: {result.get('cached')}")
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


async def test_quiz_generation():
    print("\n=== PROBANDO GENERACIÓN DE QUIZ ===\n")
    
    service = AIService()
    document_id = 1
    
    try:
        result = await service.generate_quiz(
            document_id=document_id,
            num_questions=5,
            difficulty="medium"
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Quiz generado correctamente")
            print(f"   Quiz ID: {result.get('quiz_id')}")
            print(f"   Número de preguntas: {len(result.get('questions', []))}")
            print(f"   Dificultad: {result.get('difficulty')}")
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


async def test_database_connection():
    print("\n=== PROBANDO CONEXIÓN A BASE DE DATOS ===\n")
    
    try:
        db_manager = DatabaseManager()
        session = db_manager.get_session()
        print("✅ Conexión a PostgreSQL exitosa")
        session.close()
    except Exception as e:
        print(f"❌ Error de conexión: {e}")


def test_redis_connection():
    print("\n=== PROBANDO CONEXIÓN A REDIS ===\n")
    
    try:
        from database.cache_manager import CacheManager
        cache = CacheManager()
        print("✅ Conexión a Redis exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")


async def run_all_tests():
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA ML")
    print("=" * 50)
    
    test_database_connection()
    test_redis_connection()
    
    choice = input("\n¿Deseas probar análisis de PDF? (s/n): ")
    if choice.lower() == 's':
        await test_pdf_analysis()
    
    choice = input("\n¿Deseas probar análisis de video? (s/n): ")
    if choice.lower() == 's':
        await test_video_analysis()
    
    choice = input("\n¿Deseas probar generación de quiz? (s/n): ")
    if choice.lower() == 's':
        await test_quiz_generation()
    
    print("\n" + "=" * 50)
    print("✅ PRUEBAS COMPLETADAS")


if __name__ == "__main__":
    asyncio.run(run_all_tests())