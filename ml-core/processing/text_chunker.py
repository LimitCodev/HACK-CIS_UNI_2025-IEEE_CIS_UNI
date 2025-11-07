import re
from typing import List
from config import settings


class TextChunker:
    def __init__(self):
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def chunk_text(self, text: str, max_size: int) -> List[str]:
        paragraphs = self._split_into_paragraphs(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_words = para.split()
            para_size = len(para_words)
            
            if current_size + para_size <= max_size:
                current_chunk.extend(para_words)
                current_size += para_size
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                
                if para_size > max_size:
                    sub_chunks = self._split_large_paragraph(para, max_size)
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1].split()
                    current_size = len(current_chunk)
                else:
                    current_chunk = para_words
                    current_size = para_size
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        overlapped_chunks = self._add_overlap(chunks)
        
        return overlapped_chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs
    
    def _split_large_paragraph(self, paragraph: str, max_size: int) -> List[str]:
        sentences = re.split(r'[.!?]+\s+', paragraph)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_words = sentence.split()
            sentence_size = len(sentence_words)
            
            if current_size + sentence_size <= max_size:
                current_chunk.extend(sentence_words)
                current_size += sentence_size
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = sentence_words
                current_size = sentence_size
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        if len(chunks) <= 1:
            return chunks
        
        overlapped = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_words = chunks[i-1].split()
            curr_words = chunks[i].split()
            
            overlap_words = prev_words[-self.chunk_overlap:] if len(prev_words) > self.chunk_overlap else prev_words
            
            new_chunk = " ".join(overlap_words + curr_words)
            overlapped.append(new_chunk)
        
        return overlapped