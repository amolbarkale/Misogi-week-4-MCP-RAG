# MCP Document Analyzer

A powerful MCP (Model Context Protocol) server for comprehensive document analysis including sentiment analysis, keyword extraction, readability scoring, and full-text search.

## 🚀 Features

- **Document Storage**: Store and manage documents with metadata
- **Sentiment Analysis**: Analyze document sentiment with confidence scores
- **Keyword Extraction**: Extract key terms using YAKE and TF-IDF algorithms
- **Readability Analysis**: Multiple readability metrics (Flesch, Gunning Fog, SMOG, etc.)
- **Full-Text Search**: Fast document search with relevance scoring
- **Caching**: Analysis results are cached for improved performance

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Git

### Local Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd document-alanyzer-with-mcp
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. **Initialize database**
```bash
python app/init_docs.py
```

4. **Start the server**
```bash
python -m app.server
```

The server will start on `http://localhost:8000`

### Docker Installation

1. **Build the Docker image**
```bash
docker build -t mcp-doc-analyzer .
```

2. **Run the container**
```bash
docker run -p 8000:8000 mcp-doc-analyzer
```

## 📡 MCP Tools

### 1. `analyze_document(document_id: int)`
Perform comprehensive analysis of a stored document.

**Parameters:**
- `document_id` (int): The ID of the document to analyze

**Returns:**
```json
{
  "success": true,
  "document_id": 1,
  "document_title": "Sample Document",
  "analysis": {
    "basic_statistics": {
      "word_count": 150,
      "sentence_count": 8,
      "reading_time_minutes": 0.75
    },
    "sentiment_analysis": {
      "label": "POSITIVE",
      "score": 0.95
    },
    "keyword_analysis": {
      "keywords": [
        {"keyword": "machine learning", "combined_score": 0.85},
        {"keyword": "artificial intelligence", "combined_score": 0.78}
      ]
    },
    "readability_analysis": {
      "flesch_reading_ease": 65.2,
      "interpretation": {
        "reading_level": "Standard (8th-9th grade)",
        "difficulty": "Moderate"
      }
    }
  }
}
```

### 2. `get_sentiment(text: str)`
Analyze sentiment of any text.

**Parameters:**
- `text` (str): The text to analyze

**Returns:**
```json
{
  "success": true,
  "sentiment": "POSITIVE",
  "confidence": 0.95,
  "strength": "Strong",
  "recommendation": "Strong positive sentiment - good tone"
}
```

### 3. `extract_keywords(text: str, limit: int = 10)`
Extract keywords from any text.

**Parameters:**
- `text` (str): The text to analyze
- `limit` (int): Maximum number of keywords (1-50, default: 10)

**Returns:**
```json
{
  "success": true,
  "keywords": [
    {"keyword": "machine learning", "combined_score": 0.85},
    {"keyword": "data analysis", "combined_score": 0.72}
  ],
  "method": "combined",
  "text_length": 500,
  "word_count": 95
}
```

### 4. `add_document(title: str, content: str, author: str = None)`
Add a new document to the database.

**Parameters:**
- `title` (str): Document title
- `content` (str): Document content
- `author` (str, optional): Author name

**Returns:**
```json
{
  "success": true,
  "document": {
    "id": 8,
    "title": "New Document",
    "author": "John Doe",
    "word_count": 250,
    "sentence_count": 12,
    "created_at": "2024-01-15T10:30:00"
  },
  "analysis_completed": true
}
```

### 5. `search_documents(query: str, limit: int = 10)`
Search documents using full-text search.

**Parameters:**
- `query` (str): Search query
- `limit` (int): Maximum results (1-50, default: 10)

**Returns:**
```json
{
  "success": true,
  "query": "machine learning",
  "results_count": 3,
  "documents": [
    {
      "id": 4,
      "title": "Vector Embeddings",
      "relevance_score": 0.95,
      "content_preview": "...machine learning models use vector embeddings...",
      "word_count": 2863
    }
  ]
}
```

## 🔧 HTTP Endpoints

### Health Check
- **GET** `/health` - Server health status

### MCP Protocol
- **POST** `/mcp/session` - Establish MCP session
- **GET** `/mcp/tools` - List available tools
- **POST** `/mcp/tools/call` - Call MCP tools

### Static Files
- **GET** `/static/*` - Serve static files

## 📊 Sample Data

The server comes pre-loaded with 7 sample documents covering AI and MCP topics:

1. **MCP Summary** (ID: 1) - Overview of Model Context Protocol
2. **Build Deploy MCP Server** (ID: 2) - MCP server development guide
3. **Understanding RAG** (ID: 3) - Retrieval Augmented Generation concepts
4. **Vector Embeddings** (ID: 4) - Vector embeddings in AI
5. **AI Coding Tools** (ID: 5) - AI-powered development tools
6. **LLMs and Multimodality** (ID: 6) - Large Language Models overview
7. **Advanced Prompt Techniques** (ID: 7) - Prompt engineering strategies

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python test_mcp_tools.py
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │ ──▶│   FastMCP       │ ──▶│   Document      │
│  (Cursor/etc)   │    │   Server        │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   NLP Engine    │ ◀──│   SQLite        │
                       │  (spaCy/YAKE)   │    │   Database      │
                       └─────────────────┘    └─────────────────┘
```

## 🎯 Use Cases

1. **Content Analysis**: Analyze blog posts, articles, documentation
2. **Document Management**: Store and search through document collections
3. **Writing Assistance**: Get readability scores and improvement suggestions
4. **Research**: Extract keywords and themes from large text collections
5. **Sentiment Monitoring**: Track sentiment across documents over time

## 🔒 Error Handling

All tools return consistent error responses:

```json
{
  "error": true,
  "message": "Detailed error description"
}
```

Common error scenarios:
- Invalid document IDs
- Empty text input
- Invalid parameter ranges
- Database connection issues

## 🚀 Performance

- **Analysis Caching**: Results cached in database
- **Parallel Processing**: Batch analysis support
- **Optimized Queries**: FTS indexing for fast search
- **Memory Efficient**: Streaming for large documents

## 📈 Monitoring

- Health check endpoint: `/health`
- Request logging via FastAPI
- Error tracking and reporting
- Performance metrics collection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Run the test suite
3. Review error logs
4. Open an issue on GitHub

---

**Built with FastMCP, spaCy, and SQLite for reliable document analysis.** 