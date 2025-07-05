# Document Analyzer MCP Server - Implementation Plan

## 📋 Project Analysis Summary

**Current State:**
- ✅ FastMCP server foundation with FastAPI
- ✅ Basic sentiment analysis using transformers
- ✅ Word/sentence statistics using spaCy
- ✅ 7 sample documents (AI/MCP related content)
- ✅ Docker setup configured
- ✅ Basic dependencies in requirements.txt

**Missing Components:**
- ❌ Document storage & metadata management
- ❌ Keyword extraction functionality
- ❌ Readability scoring
- ❌ Full document analysis tool
- ❌ Document search functionality
- ❌ Document addition capability
- ❌ Database layer for persistence

## 🎯 Implementation Plan

### Phase 1: Foundation & Dependencies
- [ ] **Task 1.1**: Update requirements.txt with missing dependencies
  - Add spaCy for keyword extraction
  - Add textstat for readability scoring
  - Add FTS (Full-Text Search) dependencies
  - Dependencies: None

- [ ] **Task 1.2**: Create database models for document storage
  - Design Document schema with metadata fields
  - Create SQLModel/SQLite setup
  - Add document indexing for search
  - Dependencies: Task 1.1

- [ ] **Task 1.3**: Initialize database and load sample documents
  - Create database initialization script
  - Load existing sample documents with metadata
  - Generate unique document IDs
  - Dependencies: Task 1.2

### Phase 2: Core NLP Features
- [ ] **Task 2.1**: Implement keyword extraction function
  - Add keyword extraction using spaCy/TF-IDF
  - Support configurable keyword limits
  - Filter out stop words and normalize terms
  - Dependencies: Task 1.1

- [ ] **Task 2.2**: Implement readability scoring
  - Add multiple readability metrics (Flesch, Gunning Fog, etc.)
  - Calculate reading level and complexity scores
  - Return comprehensive readability report
  - Dependencies: Task 1.1

- [ ] **Task 2.3**: Enhance NLP module with new functions
  - Integrate keyword extraction into nlp.py
  - Add readability scoring to nlp.py
  - Optimize performance for large documents
  - Dependencies: Task 2.1, Task 2.2

### Phase 3: Document Management
- [ ] **Task 3.1**: Implement document storage service
  - Create document CRUD operations
  - Add metadata handling (title, author, date, etc.)
  - Implement document validation
  - Dependencies: Task 1.2, Task 1.3

- [ ] **Task 3.2**: Implement full-text search functionality
  - Add search by content using SQLite FTS
  - Support multiple search operators
  - Rank results by relevance
  - Dependencies: Task 3.1

- [ ] **Task 3.3**: Create document analysis aggregation
  - Combine all analysis functions into single pipeline
  - Cache analysis results for performance
  - Handle analysis errors gracefully
  - Dependencies: Task 2.3, Task 3.1

### Phase 4: MCP Tools Implementation
- [ ] **Task 4.1**: Implement `analyze_document(document_id)` tool
  - Full analysis pipeline integration
  - Return comprehensive analysis results
  - Handle invalid document IDs
  - Dependencies: Task 3.3

- [ ] **Task 4.2**: Implement `extract_keywords(text, limit)` tool
  - Expose keyword extraction as MCP tool
  - Support dynamic text input
  - Validate limit parameter
  - Dependencies: Task 2.1

- [ ] **Task 4.3**: Implement `add_document(document_data)` tool
  - Support adding new documents via MCP
  - Validate document data structure
  - Auto-generate metadata
  - Dependencies: Task 3.1

- [ ] **Task 4.4**: Implement `search_documents(query)` tool
  - Expose search functionality via MCP
  - Return formatted search results
  - Support advanced search options
  - Dependencies: Task 3.2

- [ ] **Task 4.5**: Enhance existing `get_sentiment(text)` tool
  - Add confidence thresholds
  - Support batch processing
  - Improve error handling
  - Dependencies: Task 2.3

### Phase 5: Testing & Optimization
- [ ] **Task 5.1**: Create comprehensive test suite
  - Unit tests for all NLP functions
  - Integration tests for MCP tools
  - Test with sample documents
  - Dependencies: Task 4.5

- [ ] **Task 5.2**: Performance optimization
  - Optimize database queries
  - Add caching for repeated analyses
  - Implement async processing where beneficial
  - Dependencies: Task 5.1

- [ ] **Task 5.3**: Error handling & logging
  - Add comprehensive error handling
  - Implement structured logging
  - Add health check endpoints
  - Dependencies: Task 5.2

### Phase 6: Documentation & Deployment
- [ ] **Task 6.1**: Update Docker configuration
  - Optimize Docker image size
  - Add proper environment variables
  - Ensure all dependencies are installed
  - Dependencies: Task 5.3

- [ ] **Task 6.2**: Create API documentation
  - Document all MCP tools and their parameters
  - Add usage examples
  - Create testing instructions
  - Dependencies: Task 6.1

- [ ] **Task 6.3**: Final integration testing
  - Test complete workflow end-to-end
  - Verify all MCP tools work correctly
  - Test with various document types
  - Dependencies: Task 6.2

## 📊 Expected Deliverables

### MCP Tools (Final)
1. `analyze_document(document_id)` - Complete analysis report
2. `get_sentiment(text)` - Enhanced sentiment analysis
3. `extract_keywords(text, limit)` - Keyword extraction
4. `add_document(document_data)` - Document addition
5. `search_documents(query)` - Full-text search

### Database Schema
- Documents table with metadata
- Analysis results caching
- Full-text search indexes

### Analysis Features
- Sentiment analysis (positive/negative/neutral + confidence)
- Keyword extraction (configurable limits, TF-IDF scoring)
- Readability scoring (multiple metrics)
- Basic statistics (word count, sentence count, reading time)

## 🚀 Ready to Begin

**Total Tasks**: 18 tasks across 6 phases
**Estimated Effort**: 2-3 days of focused development
**Key Dependencies**: Linear progression through phases recommended

**Next Step**: Start with Phase 1 - Foundation & Dependencies to establish the core infrastructure before building analysis features. 