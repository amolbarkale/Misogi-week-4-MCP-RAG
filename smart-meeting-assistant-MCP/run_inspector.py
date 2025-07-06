#!/usr/bin/env python3
"""
Smart Meeting Assistant - Official MCP Inspector Runner

This script helps you run the official MCP Inspector to test your server.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_node():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js to use the MCP Inspector.")
        return False

def check_uv():
    """Check if uv is installed."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv found: {result.stdout.strip()}")
            return True
        else:
            print("❌ uv not found")
            return False
    except FileNotFoundError:
        print("❌ uv not found. Please install uv: pip install uv")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import fastmcp
        import sqlmodel
        import pendulum
        print("✅ All Python dependencies are installed")
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

def run_inspector():
    """Run the official MCP Inspector."""
    print("🔍 Starting Official MCP Inspector...")
    print("=" * 60)
    
    # Check Node.js
    if not check_node():
        return False
    
    # Check uv
    if not check_uv():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check database
    if not check_database():
        return False
    
    try:
        # Set environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd())
        
        # Run the official MCP Inspector
        cmd = [
            "npx", 
            "@modelcontextprotocol/inspector", 
            "fastmcp",
            "run",
            "src/main.py"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        print("=" * 60)
        print("🚀 The MCP Inspector will open in your browser automatically!")
        print("🔧 You can test all your MCP tools through the web interface.")
        print("=" * 60)
        
        subprocess.run(cmd, env=env, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Inspector failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Inspector stopped by user")
        return True
    except FileNotFoundError:
        print("❌ npx not found. Please install Node.js and npm.")
        return False

def main():
    """Main entry point."""
    print("🤖 Smart Meeting Assistant - Official MCP Inspector")
    print("=" * 60)
    
    success = run_inspector()
    
    if success:
        print("\n✅ Inspector session completed successfully!")
    else:
        print("\n❌ Inspector failed to start. Check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Make sure Node.js is installed")
        print("2. Install uv: pip install uv")
        print("3. Run: pip install -r requirements.txt")
        print("4. Run: python simple_seed.py")
        print("5. Try: fastmcp run src/main.py")

if __name__ == "__main__":
    main() 