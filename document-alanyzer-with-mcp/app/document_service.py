# app/document_service.py

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re

from .database import (
    Document, 
    get_document_by_id, 
    add_document_to_db, 
    get_all_documents,
    search_documents_fts,
    get_session
)
from .nlp import (
    analyze_text_comprehensive,
    get_word_stats,
    get_sentiment,
    extract_keywords,
    analyze_readability
)

class DocumentService:
    """Service layer for document operations"""
    
    def __init__(self):
        self.max_title_length = 200
        self.max_content_length = 1000000  # 1MB of text
        self.min_content_length = 10
    
    def validate_document_data(self, title: str, content: str, author: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate document data before storing
        
        Returns:
            Dict with 'valid' boolean and 'errors' list
        """
        errors = []
        
        # Title validation
        if not title or not title.strip():
            errors.append("Title is required")
        elif len(title) > self.max_title_length:
            errors.append(f"Title too long (max {self.max_title_length} characters)")
        
        # Content validation
        if not content or not content.strip():
            errors.append("Content is required")
        elif len(content) < self.min_content_length:
            errors.append(f"Content too short (min {self.min_content_length} characters)")
        elif len(content) > self.max_content_length:
            errors.append(f"Content too long (max {self.max_content_length} characters)")
        
        # Author validation (optional)
        if author and len(author) > 100:
            errors.append("Author name too long (max 100 characters)")
        
        # Content quality check
        if content and len(content.split()) < 5:
            errors.append("Content must contain at least 5 words")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def add_document(self, title: str, content: str, author: Optional[str] = None, 
                    source: Optional[str] = None, auto_analyze: bool = True) -> Dict[str, Any]:
        """
        Add a new document to the database
        
        Args:
            title: Document title
            content: Document content
            author: Optional author name
            source: Optional source identifier
            auto_analyze: Whether to run analysis immediately
        
        Returns:
            Dict with success status and document data or error info
        """
        try:
            # Validate input
            validation = self.validate_document_data(title, content, author)
            if not validation["valid"]:
                return {
                    "success": False,
                    "errors": validation["errors"]
                }
            
            # Clean and prepare data
            title = title.strip()
            content = content.strip()
            author = author.strip() if author else None
            source = source.strip() if source else None
            
            # Calculate basic stats
            stats = get_word_stats(content)
            
            # Add to database
            doc = add_document_to_db(
                title=title,
                content=content,
                author=author,
                source=source
            )
            
            # Update with basic stats
            with get_session() as session:
                db_doc = session.get(Document, doc.id)
                if db_doc:
                    db_doc.word_count = stats["word_count"]
                    db_doc.sentence_count = stats["sentence_count"]
                    db_doc.reading_time_minutes = stats["reading_time_minutes"]
                    db_doc.updated_at = datetime.now()
                    session.commit()
            
            # Run analysis if requested
            analysis_result = None
            if auto_analyze:
                analysis_result = self.analyze_document(doc.id)
            
            return {
                "success": True,
                "document": {
                    "id": doc.id,
                    "title": doc.title,
                    "author": doc.author,
                    "source": doc.source,
                    "word_count": stats["word_count"],
                    "sentence_count": stats["sentence_count"],
                    "reading_time_minutes": stats["reading_time_minutes"],
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat()
                },
                "analysis": analysis_result if auto_analyze else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Database error: {str(e)}"]
            }
    
    def get_document(self, document_id: int) -> Dict[str, Any]:
        """
        Get a document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Dict with document data or error info
        """
        try:
            doc = get_document_by_id(document_id)
            
            if not doc:
                return {
                    "success": False,
                    "errors": [f"Document with ID {document_id} not found"]
                }
            
            return {
                "success": True,
                "document": {
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "author": doc.author,
                    "source": doc.source,
                    "word_count": doc.word_count,
                    "sentence_count": doc.sentence_count,
                    "reading_time_minutes": doc.reading_time_minutes,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Database error: {str(e)}"]
            }
    
    def search_documents(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search documents using full-text search
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dict with search results
        """
        try:
            if not query or not query.strip():
                return {
                    "success": False,
                    "errors": ["Search query is required"]
                }
            
            # Clean query
            query = query.strip()
            
            # Perform FTS search
            results = search_documents_fts(query, limit)
            
            documents = []
            for doc in results:
                # Calculate relevance score (simplified)
                relevance_score = self._calculate_relevance(doc.content, query)
                
                documents.append({
                    "id": doc.id,
                    "title": doc.title,
                    "author": doc.author,
                    "source": doc.source,
                    "word_count": doc.word_count,
                    "sentence_count": doc.sentence_count,
                    "reading_time_minutes": doc.reading_time_minutes,
                    "relevance_score": relevance_score,
                    "content_preview": self._get_content_preview(doc.content, query),
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat()
                })
            
            return {
                "success": True,
                "query": query,
                "results_count": len(documents),
                "documents": documents
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Search error: {str(e)}"]
            }
    
    def analyze_document(self, document_id: int, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Analyze a document comprehensively
        
        Args:
            document_id: Document ID
            force_refresh: Whether to force new analysis (ignore cache)
            
        Returns:
            Dict with analysis results
        """
        try:
            # Get document
            doc_result = self.get_document(document_id)
            if not doc_result["success"]:
                return doc_result
            
            doc_data = doc_result["document"]
            content = doc_data["content"]
            
            # Check if we have cached analysis (simplified - in production, you'd check timestamps)
            if not force_refresh:
                cached_analysis = self._get_cached_analysis(document_id)
                if cached_analysis:
                    return {
                        "success": True,
                        "document_id": document_id,
                        "document_title": doc_data["title"],
                        "analysis": cached_analysis,
                        "cached": True
                    }
            
            # Run comprehensive analysis
            analysis = analyze_text_comprehensive(content)
            
            # Cache the results (simplified)
            self._cache_analysis(document_id, analysis)
            
            return {
                "success": True,
                "document_id": document_id,
                "document_title": doc_data["title"],
                "analysis": analysis,
                "cached": False
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Analysis error: {str(e)}"]
            }
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate simple relevance score"""
        try:
            query_terms = query.lower().split()
            content_lower = content.lower()
            
            matches = sum(1 for term in query_terms if term in content_lower)
            return round(matches / len(query_terms), 2) if query_terms else 0.0
        except:
            return 0.0
    
    def _get_content_preview(self, content: str, query: str, preview_length: int = 200) -> str:
        """Get content preview with query context"""
        try:
            query_terms = query.lower().split()
            
            # Find first occurrence of any query term
            content_lower = content.lower()
            first_match_pos = len(content)
            
            for term in query_terms:
                pos = content_lower.find(term)
                if pos != -1 and pos < first_match_pos:
                    first_match_pos = pos
            
            # Extract preview around the match
            start_pos = max(0, first_match_pos - preview_length // 2)
            end_pos = min(len(content), start_pos + preview_length)
            
            preview = content[start_pos:end_pos]
            
            # Add ellipsis if needed
            if start_pos > 0:
                preview = "..." + preview
            if end_pos < len(content):
                preview = preview + "..."
            
            return preview
            
        except:
            return content[:preview_length] + "..." if len(content) > preview_length else content
    
    def _get_cached_analysis(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get cached analysis (simplified implementation)"""
        try:
            doc = get_document_by_id(document_id)
            if doc and doc.sentiment_analysis:
                # In a real implementation, you'd check if cache is still valid
                return {
                    "cached_sentiment": json.loads(doc.sentiment_analysis) if doc.sentiment_analysis else None,
                    "cached_keywords": json.loads(doc.keywords) if doc.keywords else None,
                    "cached_readability": json.loads(doc.readability_scores) if doc.readability_scores else None
                }
        except:
            pass
        return None
    
    def _cache_analysis(self, document_id: int, analysis: Dict[str, Any]) -> None:
        """Cache analysis results (simplified implementation)"""
        try:
            with get_session() as session:
                doc = session.get(Document, document_id)
                if doc:
                    # Store main analysis components as JSON
                    if "sentiment_analysis" in analysis:
                        doc.sentiment_analysis = json.dumps(analysis["sentiment_analysis"])
                    if "keyword_analysis" in analysis:
                        doc.keywords = json.dumps(analysis["keyword_analysis"])
                    if "readability_analysis" in analysis:
                        doc.readability_scores = json.dumps(analysis["readability_analysis"])
                    
                    doc.updated_at = datetime.now()
                    session.commit()
        except Exception as e:
            print(f"Cache error: {e}")

# Global service instance
document_service = DocumentService() 