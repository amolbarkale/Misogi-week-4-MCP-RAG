# Smart Meeting Assistant - Official MCP Inspector (PowerShell)
# This script runs the official MCP Inspector for testing

Write-Host ""
Write-Host "🤖 Smart Meeting Assistant - Official MCP Inspector" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Gray
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js to use the MCP Inspector." -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python not found. Please install Python." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if database exists
if (-not (Test-Path "meetings.db")) {
    Write-Host "❌ Database not found. Please run: python simple_seed.py" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ All requirements met" -ForegroundColor Green
Write-Host ""
Write-Host "🔍 Starting Official MCP Inspector..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Gray
Write-Host "🚀 The MCP Inspector will open in your browser automatically!" -ForegroundColor Green
Write-Host "🔧 You can test all your MCP tools through the web interface." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Gray
Write-Host ""

# Set environment and run the inspector
$env:PYTHONPATH = $PWD.Path

try {
    npx @modelcontextprotocol/inspector fastmcp run src/main.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Inspector session completed successfully!" -ForegroundColor Green
    } else {
        throw "Inspector failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host ""
    Write-Host "❌ Inspector failed to start. Check the error messages above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Make sure Node.js is installed" -ForegroundColor White
    Write-Host "2. Run: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "3. Run: python simple_seed.py" -ForegroundColor White
    Write-Host "4. Try: fastmcp run src/main.py" -ForegroundColor White
    
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to exit" 