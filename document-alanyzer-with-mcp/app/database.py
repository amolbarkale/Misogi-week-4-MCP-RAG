# app/database.py

from sqlmodel import SQLModel, Field, create_engine, Session, select, text
from typing import Optional, List
from datetime import datetime
import json

# Database Models
class Document(SQLModel, table=True):
    """Document model for storing text documents with metadata"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)                    # Document title
    content: str                                      # Full text content
    author: Optional[str] = Field(default=None)       # Document author
    source: Optional[str] = Field(default=None)       # Source file path
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Metadata fields
    word_count: Optional[int] = Field(default=None)
    sentence_count: Optional[int] = Field(default=None)
    reading_time_minutes: Optional[float] = Field(default=None)
    
    # Analysis cache (JSON stored as string)
    sentiment_analysis: Optional[str] = Field(default=None)
    keywords: Optional[str] = Field(default=None)
    readability_scores: Optional[str] = Field(default=None)

class DocumentAnalysis(SQLModel, table=True):
    """Separate table for caching analysis results"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    analysis_type: str = Field(index=True)            # "sentiment", "keywords", "readability"
    analysis_data: str                                # JSON data
    created_at: datetime = Field(default_factory=datetime.now)

# Database Setup
DATABASE_URL = "sqlite:///./documents.db"

# Create engine with FTS support
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    connect_args={
        "check_same_thread": False,  # Needed for SQLite
        "timeout": 30                # 30 second timeout
    }
)

def init_database():
    """Initialize database and create tables"""
    SQLModel.metadata.create_all(engine)
    
    # Enable FTS (Full-Text Search) for documents
    with Session(engine) as session:
        # Create FTS virtual table for content search
        session.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS document_fts USING fts5(
                title, content, author, content='document', content_rowid='id'
            )
        """))
        
        # Create trigger to sync FTS table
        session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS document_fts_sync_insert AFTER INSERT ON document
            BEGIN
                INSERT INTO document_fts(rowid, title, content, author) 
                VALUES (new.id, new.title, new.content, new.author);
            END
        """))
        
        session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS document_fts_sync_update AFTER UPDATE ON document
            BEGIN
                UPDATE document_fts SET title=new.title, content=new.content, author=new.author 
                WHERE rowid=new.id;
            END
        """))
        
        session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS document_fts_sync_delete AFTER DELETE ON document
            BEGIN
                DELETE FROM document_fts WHERE rowid=old.id;
            END
        """))
        
        session.commit()
        print("✅ Database initialized with FTS support")

def get_session():
    """Get database session"""
    return Session(engine)

# Database utility functions
def get_document_by_id(document_id: int) -> Optional[Document]:
    """Get document by ID"""
    with get_session() as session:
        return session.get(Document, document_id)

def search_documents_fts(query: str, limit: int = 10) -> List[Document]:
    """Search documents using Full-Text Search"""
    with get_session() as session:
        # FTS search query
        stmt = session.execute(text("""
            SELECT d.* FROM document d
            JOIN document_fts fts ON d.id = fts.rowid
            WHERE document_fts MATCH :query
            ORDER BY rank
            LIMIT :limit
        """), {"query": query, "limit": limit})
        
        results = []
        for row in stmt.fetchall():
            # Convert row to Document object
            doc_data = dict(zip(row.keys(), row))
            results.append(Document(**doc_data))
        
        return results

def add_document_to_db(title: str, content: str, author: Optional[str] = None, source: Optional[str] = None) -> Document:
    """Add new document to database"""
    with get_session() as session:
        doc = Document(
            title=title,
            content=content,
            author=author,
            source=source
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc

def get_all_documents() -> List[Document]:
    """Get all documents"""
    with get_session() as session:
        return list(session.exec(select(Document)).all()) 