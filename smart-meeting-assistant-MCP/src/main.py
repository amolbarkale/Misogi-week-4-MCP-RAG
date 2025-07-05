"""
Smart Meeting Assistant - Main MCP Server

This is the main entry point for our FastMCP server. It defines all the MCP tools
that Claude Desktop can use to interact with our meeting management system.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize FastMCP app
app = FastMCP("Smart Meeting Assistant")

# Pydantic models for type validation
class MeetingCreate(BaseModel):
    title: str = Field(..., description="Meeting title")
    participants: List[str] = Field(..., description="List of participant email addresses")
    duration: int = Field(..., description="Meeting duration in minutes")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Meeting preferences")

class MeetingResponse(BaseModel):
    meeting_id: str
    title: str
    participants: List[str]
    duration: int
    status: str
    created_at: datetime

# Our first MCP tool!
@app.tool()
def create_meeting(
    title: str,
    participants: List[str],
    duration: int,
    preferences: Optional[Dict[str, Any]] = None
) -> MeetingResponse:
    """
    Create a new meeting with intelligent scheduling.
    
    Args:
        title: The meeting title
        participants: List of participant email addresses
        duration: Meeting duration in minutes
        preferences: Optional meeting preferences (timezone, preferred times, etc.)
    
    Returns:
        Meeting details with assigned ID and status
    """
    # For now, we'll create a simple mock response
    # Later we'll integrate with database and scheduling logic
    
    meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return MeetingResponse(
        meeting_id=meeting_id,
        title=title,
        participants=participants,
        duration=duration,
        status="created",
        created_at=datetime.now()
    )

# Health check endpoint
@app.tool()
def health_check() -> Dict[str, str]:
    """Check if the MCP server is running properly."""
    return {
        "status": "healthy",
        "server": "Smart Meeting Assistant MCP",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }

# Server info
@app.tool()
def get_server_info() -> Dict[str, Any]:
    """Get information about the Smart Meeting Assistant server."""
    return {
        "name": "Smart Meeting Assistant",
        "version": "0.1.0",
        "description": "AI-powered meeting scheduling and analysis",
        "tools": [
            "create_meeting",
            "find_optimal_slots", 
            "detect_scheduling_conflicts",
            "analyze_meeting_patterns",
            "generate_agenda_suggestions",
            "calculate_workload_balance",
            "score_meeting_effectiveness",
            "optimize_meeting_schedule"
        ],
        "features": [
            "Intelligent scheduling",
            "Conflict detection",
            "AI-powered analysis",
            "Multi-timezone support",
            "Meeting effectiveness scoring"
        ]
    }

if __name__ == "__main__":
    # This will be used for testing
    print("Smart Meeting Assistant MCP Server")
    print("Use: fastmcp run src.main:app") 