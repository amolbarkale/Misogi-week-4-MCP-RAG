"""
Smart Meeting Assistant - Main MCP Server

This is the main entry point for our FastMCP server. It defines all the MCP tools
that Claude Desktop can use to interact with our meeting management system.
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import our modules
from src.database import init_database, db_manager, UserService, MeetingService
from src.scheduler import find_optimal_meeting_slots, detect_scheduling_conflicts
from src.models import MeetingStatus, MeetingType, MeetingCreate as MeetingCreateModel

# Initialize FastMCP app
app = FastMCP("Smart Meeting Assistant")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database on startup
try:
    init_database()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    raise

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
    try:
        # Create meeting data object
        meeting_data = MeetingCreateModel(
            title=title,
            start_time=datetime.now(),  # For now, just use current time
            duration_minutes=duration,
            participants=participants,
            meeting_type=MeetingType.TEAM_MEETING,
            description=f"Meeting scheduled with {len(participants)} participants"
        )
        
        # Use first participant as organizer for now
        organizer_id = participants[0] if participants else "default@example.com"
        
        # Create meeting using the service
        meeting_id = MeetingService.create_meeting(meeting_data, organizer_id)
        
        # Get the created meeting details
        meeting = MeetingService.get_meeting_by_id(meeting_id)
        if not meeting:
            raise ValueError("Failed to retrieve created meeting")
        
        return MeetingResponse(
            meeting_id=str(meeting_id),
            title=meeting.title,
            participants=meeting.participants,
            duration=meeting.duration_minutes,
            status=meeting.status.value,
            created_at=meeting.created_at
        )
    
    except Exception as e:
        logger.error(f"Error creating meeting: {e}")
        # Return error response instead of raising
        return MeetingResponse(
            meeting_id="error",
            title=title,
            participants=participants,
            duration=duration,
            status="error",
            created_at=datetime.now()
        )

# Health check endpoint
@app.tool()
def health_check() -> Dict[str, Any]:
    """Check if the MCP server is running properly."""
    try:
        # Test database connection
        with db_manager.get_session() as session:
            user_service = UserService()
            # Simple query to test database
            users = user_service.get_all_users()
            
        return {
            "status": "healthy",
            "server": "Smart Meeting Assistant MCP",
            "version": "0.1.0",
            "database": "connected",
            "users_count": len(users),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "server": "Smart Meeting Assistant MCP",
            "version": "0.1.0",
            "database": "disconnected",
            "error": str(e),
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
    print("Use: fastmcp run src/main.py") 