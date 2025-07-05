# MCP Inspector Architecture

## Development & Testing Workflow

The MCP Inspector provides a local testing environment for MCP servers without requiring external MCP clients.

## Architecture with Inspector

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Developer] --> INSP[MCP Inspector<br/>Web Interface<br/>localhost:3000]
        DEV --> CONFIG[mcp_inspector_config.json]
    end
    
    subgraph "Local Testing"
        INSP --> SERVER[Document Analyzer Server<br/>MCP Server]
        INSP --> TOOLS[Tool Testing Interface]
        INSP --> DEBUG[Debug Console]
        INSP --> LOGS[Error Logs & Monitoring]
    end
    
    subgraph "Available Tools"
        SERVER --> T1[analyze_document]
        SERVER --> T2[get_sentiment]
        SERVER --> T3[extract_keywords]
        SERVER --> T4[add_document]
        SERVER --> T5[search_documents]
    end
    
    subgraph "Database"
        SERVER --> DB[(SQLite Database)]
        DB --> DOCS[Sample Documents]
        DB --> FTS[Full-Text Search]
    end
    
    TOOLS --> T1
    TOOLS --> T2
    TOOLS --> T3
    TOOLS --> T4
    TOOLS --> T5
    
    classDef dev fill:#e1f5fe
    classDef inspector fill:#f3e5f5
    classDef server fill:#e8f5e8
    classDef tools fill:#fff3e0
    classDef database fill:#fce4ec
    
    class DEV,CONFIG dev
    class INSP,TOOLS,DEBUG,LOGS inspector
    class SERVER server
    class T1,T2,T3,T4,T5 tools
    class DB,DOCS,FTS database
```

## Testing Workflow

1. **Start Inspector**: Run `run_inspector.ps1` or `run_inspector.bat`
2. **Access Web Interface**: Open `http://localhost:3000`
3. **Test Tools**: Use the web interface to test all 5 MCP tools
4. **Debug Issues**: View errors and performance metrics
5. **Iterate**: Fix issues and retest without external dependencies

## Production vs Development

### Development (with Inspector)
- Local testing environment
- Immediate feedback on tool functionality
- Error debugging and performance monitoring
- No external dependencies required

### Production (with Claude/Cursor)
- Real MCP client integration
- User-facing functionality
- Hosted server deployment
- External MCP host connections

## Inspector Features

### Tool Testing
- **Interactive Forms**: Test tools with custom parameters
- **Sample Data**: Pre-loaded test cases and examples
- **Result Validation**: Verify tool outputs and formats
- **Parameter Validation**: Test input validation and error handling

### Debugging
- **Error Messages**: Detailed error information and stack traces
- **Performance Metrics**: Tool execution times and resource usage
- **Connection Status**: MCP server connectivity monitoring
- **Protocol Validation**: Verify MCP protocol compliance

### Development Aid
- **Schema Validation**: Ensure tool schemas are correct
- **Documentation**: View tool descriptions and parameters
- **Testing History**: Track previous test results
- **Configuration**: Easy server configuration management

This architecture allows you to develop and test your MCP server completely locally before deploying to production environments. 