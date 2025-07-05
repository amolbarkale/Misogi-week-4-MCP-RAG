# app/server.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastmcp import FastMCP
import nlp
from database import init_database
from document_service import document_service
import os
from pathlib import Path
from typing import Optional

# 1) Create your FastAPI app and mount "data/static"
api = FastAPI(title="Doc-Analyzer")

# Mount static files with proper path handling
static_dir = Path("data/static")
if static_dir.exists() and static_dir.is_dir():
    api.mount(
        "/static",
        StaticFiles(directory=str(static_dir)),
        name="static",
    )
    print(f"Static files mounted from: {static_dir.absolute()}")
else:
    print(f"Warning: Static directory not found: {static_dir.absolute()}")

# Add health check endpoint
@api.get("/health")
def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {"status": "healthy", "service": "MCP Document Analyzer"}

# 2) Wrap that FastAPI app in FastMCP
#    (this will auto-generate /mcp/…, /tools/…, etc. on your FastAPI instance)
mcp = FastMCP.from_fastapi(api, name="Doc-Analyzer")  # ✨ note: from_fastapi, not the ctor

@mcp.tool
def get_sentiment(text: str) -> dict:
    """
    Analyze sentiment of any text.
    
    Returns sentiment label (POSITIVE/NEGATIVE), confidence score, and interpretation.
    """
    if not text or not text.strip():
        return {
            "error": True,
            "message": "Text is required"
        }
    
    # Get basic sentiment
    sentiment = nlp.get_sentiment(text)
    
    # Add enhanced features
    enhanced_result = {
        "success": True,
        "sentiment": sentiment["label"],
        "confidence": sentiment["score"],
        "text_length": len(text),
        "word_count": len(text.split())
    }
    
    # Add interpretation
    if sentiment["score"] >= 0.8:
        enhanced_result["strength"] = "Strong"
    elif sentiment["score"] >= 0.6:
        enhanced_result["strength"] = "Moderate"
    else:
        enhanced_result["strength"] = "Weak"
    
    # Add recommendation
    if sentiment["label"] == "NEGATIVE" and sentiment["score"] > 0.7:
        enhanced_result["recommendation"] = "Strong negative sentiment detected - consider review"
    elif sentiment["label"] == "POSITIVE" and sentiment["score"] > 0.7:
        enhanced_result["recommendation"] = "Strong positive sentiment - good tone"
    else:
        enhanced_result["recommendation"] = "Neutral or mixed sentiment"
    
    return enhanced_result

@mcp.tool
def basic_stats(text: str) -> dict:
    """Return word & sentence count."""
    return nlp.get_word_stats(text)

@mcp.tool
def analyze_document(document_id: int) -> dict:
    """
    Perform comprehensive analysis of a document by ID.
    
    Returns complete analysis including sentiment, keywords, readability, and statistics.
    """
    result = document_service.analyze_document(document_id)
    
    if not result["success"]:
        return {
            "error": True,
            "message": "; ".join(result.get("errors", ["Unknown error"]))
        }
    
    return {
        "success": True,
        "document_id": result["document_id"],
        "document_title": result["document_title"],
        "analysis": result["analysis"],
        "cached": result.get("cached", False)
    }

@mcp.tool
def extract_keywords(text: str, limit: int = 10) -> dict:
    """
    Extract keywords from any text.
    
    Args:
        text: Text to analyze
        limit: Maximum number of keywords to return (default: 10)
    """
    if not text or not text.strip():
        return {
            "error": True,
            "message": "Text is required"
        }
    
    if limit < 1 or limit > 50:
        return {
            "error": True,
            "message": "Limit must be between 1 and 50"
        }
    
    result = nlp.extract_keywords(text, limit)
    
    if "error" in result:
        return {
            "error": True,
            "message": result["error"]
        }
    
    return {
        "success": True,
        "keywords": result["keywords"],
        "method": result["method"],
        "text_length": result["text_length"],
        "word_count": result["word_count"]
    }

@mcp.tool
def add_document(title: str, content: str, author: Optional[str] = None) -> dict:
    """
    Add a new document to the database.
    
    Args:
        title: Document title
        content: Document content
        author: Optional author name
    """
    result = document_service.add_document(
        title=title,
        content=content,
        author=author,
        auto_analyze=True  # Run analysis automatically
    )
    
    if not result["success"]:
        return {
            "error": True,
            "message": "; ".join(result.get("errors", ["Unknown error"]))
        }
    
    return {
        "success": True,
        "document": result["document"],
        "analysis_completed": result["analysis"] is not None
    }

@mcp.tool
def search_documents(query: str, limit: int = 10) -> dict:
    """
    Search documents by content using full-text search.
    
    Args:
        query: Search query
        limit: Maximum number of results (default: 10)
    """
    if not query or not query.strip():
        return {
            "error": True,
            "message": "Search query is required"
        }
    
    if limit < 1 or limit > 50:
        return {
            "error": True,
            "message": "Limit must be between 1 and 50"
        }
    
    result = document_service.search_documents(query, limit)
    
    if not result["success"]:
        return {
            "error": True,
            "message": "; ".join(result.get("errors", ["Unknown error"]))
        }
    
    return {
        "success": True,
        "query": result["query"],
        "results_count": result["results_count"],
        "documents": result["documents"]
    }

if __name__ == "__main__":
    # Initialize database before starting server
    print("🗄️ Initializing database...")
    init_database()
    
    # 3) Start in HTTP mode, host & port can be customized
    mcp.run(transport="http", host="0.0.0.0", port=8000)
