from sqlalchemy.orm import Session as DBSession
from database.models import Session, Document
from datetime import datetime, timedelta
import hashlib
import uuid
from typing import Optional


class SessionHandler:
    def __init__(self, db: DBSession, redis_client):
        self.db = db
        self.redis = redis_client
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> uuid.UUID:
        if session_id:
            try:
                session_uuid = uuid.UUID(session_id)
                session = self.db.query(Session).filter(
                    Session.session_id == session_uuid
                ).first()
                
                if session:
                    session.last_activity = datetime.utcnow()
                    self.db.commit()
                    return session.session_id
            except (ValueError, AttributeError):
                pass
        
        new_session = Session()
        self.db.add(new_session)
        self.db.commit()
        return new_session.session_id
    
    def get_session_history(self, session_id: uuid.UUID, limit: int = 50) -> list:
        documents = self.db.query(Document).filter(
            Document.session_id == session_id
        ).order_by(Document.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": doc.id,
                "type": doc.doc_type,
                "title": doc.title,
                "summary_short": doc.summary_short,
                "created_at": doc.created_at.isoformat(),
                "source_url": doc.source_url
            }
            for doc in documents
        ]
    
    def check_duplicate(self, content: str, session_id: uuid.UUID) -> Optional[Document]:
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        existing = self.db.query(Document).filter(
            Document.content_hash == content_hash,
            Document.session_id == session_id
        ).first()
        
        return existing
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        deleted = self.db.query(Session).filter(
            Session.last_activity < cutoff
        ).delete()
        
        self.db.commit()
        return deleted