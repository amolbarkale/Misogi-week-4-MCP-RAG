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

## 🔍 MCP Inspector for Testing & Debugging

The MCP Inspector provides a web interface to test and debug your MCP server without needing external tools like Claude or Cursor.

### Quick Start with Inspector

**Option 1: PowerShell (Recommended for Windows)**
```powershell
.\run_inspector.ps1
```

**Option 2: Command Prompt**
```cmd
run_inspector.bat
```

**Option 3: Python Script**
```bash
python run_inspector.py
```

### Manual Inspector Setup

1. **Install MCP Inspector**
```bash
pip install mcp-inspector
```

2. **Start the Inspector**
```bash
mcp-inspector --config mcp_inspector_config.json
```

3. **Access the Inspector**
   - Open your browser to `http://localhost:3000`
   - The inspector will automatically connect to your Document Analyzer server
   - Test all 5 tools directly in the web interface

### What You Can Test

- **analyze_document**: Test document analysis with sample documents
- **get_sentiment**: Try sentiment analysis on different text samples
- **extract_keywords**: Test keyword extraction with various parameters
- **add_document**: Add new documents and see them analyzed
- **search_documents**: Test full-text search functionality

### Debugging Features

- **Tool Validation**: Verify all tools are properly registered
- **Error Inspection**: See detailed error messages and stack traces
- **Performance Monitoring**: Monitor tool execution times
- **Resource Testing**: Test server resources and capabilities

### Docker Installation

1. **Build the Docker image**
```bash
docker build -t mcp-doc-analyzer .
```

2. **Run the container**
```bash
docker run -p 8000:8000 mcp-doc-analyzer
```

## 🎯 Cursor IDE Integration

Integrate your Document Analyzer with Cursor IDE to use document analysis tools directly in your development environment.

### Quick Setup

**Option 1: Automatic Setup (Recommended)**
```powershell
# Windows PowerShell
.\setup_cursor_mcp.ps1
```

**Option 2: Python Script (Cross-platform)**
```bash
python setup_cursor_mcp.py
```

### Manual Setup

1. **Open Cursor Settings**
   - Go to: `Cursor Settings > Features > MCP`
   - Click: `+ Add New MCP Server`

2. **Configure Server**
   - **Name**: `document-analyzer`
   - **Type**: `stdio`
   - **Command**: `python /path/to/your/project/app/server.py`

3. **Save and Restart Cursor IDE**

### Usage in Cursor

Once configured, use these commands in Cursor's Composer:

- **Document Analysis**: "Analyze document 1 for sentiment and keywords"
- **Sentiment Analysis**: "Get sentiment of this text: [your text]"
- **Keyword Extraction**: "Extract keywords from: [your text]"
- **Document Search**: "Search for documents about machine learning"
- **Add Documents**: "Add this document to the database: [title] [content]"

### Features in Cursor

- **5 MCP Tools**: All document analysis tools available
- **Natural Language**: Use tools with conversational commands
- **Workflow Integration**: Analyze code comments, documentation, etc.
- **Real-time Analysis**: Instant feedback on text analysis

For detailed setup instructions, see [CURSOR_INTEGRATION.md](CURSOR_INTEGRATION.md)

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