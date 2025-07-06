#!/usr/bin/env python3
"""
Smart Meeting Assistant MCP Server Startup Script

This script helps you easily start the MCP server for Claude Desktop integration.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import fastmcp
        import sqlmodel
        import pendulum
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_database():
    """Check if the database exists."""
    db_path = Path("meetings.db")
    if db_path.exists():
        print("✅ Database found")
        return True
    else:
        print("❌ Database not found")
        print("Please run: python simple_seed.py")
        return False

def run_server():
    """Run the MCP server."""
    print("🚀 Starting Smart Meeting Assistant MCP Server...")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check database
    if not check_database():
        return False
    
    try:
        # Set PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd())
        
        # Run the server
        cmd = ["fastmcp", "run", "src/main.py"]
        print(f"Running command: {' '.join(cmd)}")
        print("=" * 60)
        
        subprocess.run(cmd, env=env, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return True

def main():
    """Main entry point."""
    print("🤖 Smart Meeting Assistant MCP Server")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "inspector":
        # Run with official MCP Inspector
        print("🔍 Starting with Official MCP Inspector...")
        print("Use: npx @modelcontextprotocol/inspector fastmcp run src/main.py")
        print("This will open the inspector in your browser automatically.")
        return
    else:
        # Run the server
        run_server()

if __name__ == "__main__":
    main() 