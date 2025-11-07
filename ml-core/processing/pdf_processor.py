import PyPDF2
import pdfplumber
import re
from pathlib import Path


class PDFProcessor:
    def __init__(self):
        self.max_file_size_mb = 50
    
    def extract_text(self, file_path: str) -> str:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"El archivo {file_path} no existe")
        
        if file_path.stat().st_size > self.max_file_size_mb * 1024 * 1024:
            raise ValueError(f"El archivo excede el tamaño máximo de {self.max_file_size_mb}MB")
        
        try:
            text = self._extract_with_pdfplumber(file_path)
            if not text or len(text) < 100:
                text = self._extract_with_pypdf2(file_path)
        except Exception as e:
            print(f"Error con pdfplumber, intentando con PyPDF2: {e}")
            text = self._extract_with_pypdf2(file_path)
        
        text = self._clean_text(text)
        
        return text
    
    def _extract_with_pdfplumber(self, file_path: Path) -> str:
        text_parts = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return "\n\n".join(text_parts)
    
    def _extract_with_pypdf2(self, file_path: Path) -> str:
        text_parts = []
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return "\n\n".join(text_parts)
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text
    
    def get_page_count(self, file_path: str) -> int:
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            print(f"Error al contar páginas: {e}")
            return 0