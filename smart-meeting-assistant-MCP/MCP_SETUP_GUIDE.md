# Smart Meeting Assistant MCP Setup Guide

## Overview
This guide will help you connect your Smart Meeting Assistant MCP server to Claude Desktop for local testing and integration.

## Prerequisites
- Python 3.9+
- Node.js (for the MCP Inspector)
- FastMCP CLI (included with fastmcp package)
- Claude Desktop app installed
- Virtual environment activated
- Dependencies installed (`pip install -r requirements.txt`)

## Step 1: Test MCP Server Locally

### Using the Official MCP Inspector
Use the official MCP Inspector from the Model Context Protocol documentation:

```bash
# Test the MCP server using the official inspector (locally developed server)
npx @modelcontextprotocol/inspector fastmcp run src/main.py

# Alternative: Use FastMCP dev mode (includes MCP Inspector)
fastmcp dev src/main.py
```

The official MCP Inspector provides:
- ✅ **Tools tab**: Interactive testing of all MCP tools
- 🔍 **Resources tab**: Browse and inspect available resources  
- 📝 **Prompts tab**: Test prompt templates with custom arguments
- 📡 **Notifications pane**: View server logs and notifications
- 🔗 **Server connection pane**: Configure transport and environment

### Using the Server Runner
Start the MCP server for Claude Desktop:

```bash
# Start the MCP server
python run_mcp_server.py

# Or use fastmcp directly
python -m fastmcp run src.main:app
```

## Step 2: Claude Desktop Configuration

### Find Claude Desktop Config Location
Claude Desktop stores its configuration in different locations:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Add MCP Server Configuration
Copy the contents of `claude_desktop_config.json` to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "smart-meeting-assistant": {
      "command": "python",
      "args": [
        "-m", "fastmcp", "run", "src.main:app"
      ],
      "cwd": "/c%3A/Users/Amol%20Barkale/Desktop/MisogiAI/week-4/smart-meeting-assistant-MCP",
      "env": {
        "PYTHONPATH": "/c%3A/Users/Amol%20Barkale/Desktop/MisogiAI/week-4/smart-meeting-assistant-MCP"
      }
    }
  }
}
```

**Important:** Update the `cwd` path to match your actual project directory!

## Step 3: Required Tokens

### 1. MCP Inspector Token
The MCP Inspector doesn't require a separate token - it's a local testing tool that directly interacts with your MCP server.

### 2. OpenAI API Token (for AI features)
For AI-powered features, you'll need an OpenAI API key:

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Set it as an environment variable:

```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-api-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# macOS/Linux
export OPENAI_API_KEY=your-api-key-here
```

Or add it to your project's `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

## Step 4: Restart Claude Desktop

1. **Close Claude Desktop completely**
2. **Restart Claude Desktop**
3. **Check for MCP connection** - you should see the Smart Meeting Assistant tools available

## Step 5: Test Integration

### In Claude Desktop
Try these commands to test the integration:

```
Can you check if the Smart Meeting Assistant is working?
```

```
Create a meeting titled "Team Standup" with participants alice@example.com and bob@example.com for 30 minutes
```

```
What tools are available in the Smart Meeting Assistant?
```

### Using the Official MCP Inspector
Test all tools locally using the official inspector:

```bash
npx @modelcontextprotocol/inspector fastmcp run src/main.py
```

The inspector will open in your browser and provide:
- **Tools tab**: Test `create_meeting`, `health_check`, and `get_server_info` 
- **Server connection**: Monitor connection status and logs
- **Interactive testing**: Fill out tool parameters and see results
- **Error debugging**: View detailed error messages and stack traces

## Available MCP Tools

Currently implemented:
1. ✅ `create_meeting` - Create new meetings
2. ✅ `health_check` - Server health verification
3. ✅ `get_server_info` - Server information

Planned (coming soon):
4. 🔄 `find_optimal_slots` - Find optimal meeting times
5. 🔄 `detect_scheduling_conflicts` - Detect conflicts
6. 🔄 `analyze_meeting_patterns` - Pattern analysis
7. 🔄 `generate_agenda_suggestions` - AI agenda generation
8. 🔄 `calculate_workload_balance` - Workload balancing
9. 🔄 `score_meeting_effectiveness` - Effectiveness scoring
10. 🔄 `optimize_meeting_schedule` - Schedule optimization

## Troubleshooting

### Common Issues

**1. MCP Server Not Starting**
```bash
# Install uv if not already installed
pip install uv

# Check dependencies
pip install -r requirements.txt

# Check database
python simple_seed.py

# Test manually
python -m fastmcp run src.main:app
```

**2. Claude Desktop Not Finding MCP Server**
- Verify the `cwd` path in `claude_desktop_config.json` is correct
- Ensure Claude Desktop is completely restarted
- Check that Python is in your PATH

**3. Tool Not Working**
- Use the MCP Inspector to test locally first
- Check server logs for errors
- Verify the tool parameters match the expected format

**4. AI Features Not Working**
- Ensure `OPENAI_API_KEY` is set
- Check your OpenAI API credits
- Verify the API key has the correct permissions

### Debug Commands

```bash
# Test server startup with official inspector
npx @modelcontextprotocol/inspector fastmcp run src/main.py

# Test server manually
fastmcp run src/main.py

# Check database
python simple_seed.py

# Verify dependencies
pip list | grep -E "(fastmcp|sqlmodel|pendulum)"
```

## Next Steps

Once the MCP server is connected to Claude Desktop:

1. **Test basic functionality** with the 3 current tools
2. **Implement remaining 7 tools** one by one
3. **Add AI features** for intelligent scheduling
4. **Enhance with real-time conflict detection**
5. **Add meeting analytics and insights**

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Use the MCP Inspector for local testing
3. Verify your Claude Desktop configuration
4. Ensure all dependencies are installed

The MCP server is now ready for Claude Desktop integration! 🚀 