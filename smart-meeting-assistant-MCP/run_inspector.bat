@echo off
REM Smart Meeting Assistant - Official MCP Inspector (Windows)
REM This batch file runs the official MCP Inspector for testing

echo.
echo 🤖 Smart Meeting Assistant - Official MCP Inspector
echo ============================================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js to use the MCP Inspector.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python.
    pause
    exit /b 1
)

REM Check if database exists
if not exist "meetings.db" (
    echo ❌ Database not found. Please run: python simple_seed.py
    pause
    exit /b 1
)

echo ✅ All requirements met
echo.
echo 🔍 Starting Official MCP Inspector...
echo ============================================================
echo 🚀 The MCP Inspector will open in your browser automatically!
echo 🔧 You can test all your MCP tools through the web interface.
echo ============================================================
echo.

REM Set environment and run the inspector
set PYTHONPATH=%CD%
npx @modelcontextprotocol/inspector fastmcp run src/main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Inspector failed to start. Check the error messages above.
    echo.
    echo Troubleshooting:
    echo 1. Make sure Node.js is installed
    echo 2. Run: pip install -r requirements.txt
    echo 3. Run: python simple_seed.py
    echo 4. Try: fastmcp run src/main.py
    pause
    exit /b 1
)

echo.
echo ✅ Inspector session completed successfully!
pause 