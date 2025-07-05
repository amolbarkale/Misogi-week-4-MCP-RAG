#!/usr/bin/env python3
# test_mcp_tools.py - Test script for MCP tools

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.nlp import get_sentiment, extract_keywords, analyze_readability
from app.document_service import document_service
from app.database import get_all_documents

def test_sentiment_analysis():
    """Test sentiment analysis"""
    print("🧪 Testing Sentiment Analysis...")
    
    test_texts = [
        "This MCP server is absolutely amazing and works perfectly!",
        "I hate bugs and this software is terrible.",
        "The weather is okay today, nothing special."
    ]
    
    for text in test_texts:
        result = get_sentiment(text)
        print(f"  Text: '{text[:50]}...'")
        print(f"  Sentiment: {result['label']} (confidence: {result['score']})")
        print()

def test_keyword_extraction():
    """Test keyword extraction"""
    print("🔍 Testing Keyword Extraction...")
    
    text = """
    Machine learning and artificial intelligence are revolutionizing 
    how we process and analyze large datasets. Natural language processing 
    enables computers to understand human language, while deep learning 
    algorithms can identify complex patterns in data.
    """
    
    result = extract_keywords(text, limit=5)
    print(f"  Text length: {result['text_length']} characters")
    print(f"  Method: {result['method']}")
    print("  Top keywords:")
    for kw in result['keywords'][:5]:
        print(f"    - {kw['keyword']} (score: {kw.get('combined_score', kw.get('relevance', 0))})")
    print()

def test_document_operations():
    """Test document operations"""
    print("📄 Testing Document Operations...")
    
    # Test listing existing documents
    docs = get_all_documents()
    print(f"  Found {len(docs)} existing documents")
    
    if docs:
        # Test document analysis
        first_doc = docs[0]
        print(f"  Analyzing document: '{first_doc.title}'")
        
        result = document_service.analyze_document(first_doc.id)
        if result["success"]:
            analysis = result["analysis"]
            if "basic_statistics" in analysis:
                stats = analysis["basic_statistics"]
                print(f"    Word count: {stats['word_count']}")
                print(f"    Reading time: {stats['reading_time_minutes']} minutes")
            
            if "sentiment_analysis" in analysis:
                sentiment = analysis["sentiment_analysis"]
                print(f"    Sentiment: {sentiment['label']} ({sentiment['score']})")
        else:
            print(f"    Analysis failed: {result.get('errors', [])}")
    
    # Test search
    search_result = document_service.search_documents("MCP")
    print(f"  Search for 'MCP': found {search_result.get('results_count', 0)} results")
    print()

def main():
    """Run all tests"""
    print("🚀 Testing MCP Document Analyzer Tools")
    print("=" * 50)
    
    try:
        # Test individual NLP functions
        test_sentiment_analysis()
        test_keyword_extraction()
        
        # Test document operations
        test_document_operations()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 