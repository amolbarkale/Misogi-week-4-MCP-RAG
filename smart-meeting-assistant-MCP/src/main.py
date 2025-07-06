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

# Load environment variables from .env files
from dotenv import load_dotenv
load_dotenv()  # Load .env file
load_dotenv('.env.local')  # Load .env.local file (takes precedence)

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import our modules
from src.database import init_database, db_manager, UserService, MeetingService, MeetingInsightService
from src.scheduler import find_optimal_meeting_slots, detect_scheduling_conflicts as detect_conflicts_engine
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

# AI Feature #4: Find Optimal Meeting Slots
@app.tool()
def find_optimal_slots(
    participants: List[str],
    duration_minutes: int,
    date_range_start: str,
    date_range_end: str,
    max_suggestions: int = 5
) -> List[Dict[str, Any]]:
    """
    Find optimal meeting time slots for given participants.
    
    Args:
        participants: List of participant email addresses
        duration_minutes: Meeting duration in minutes
        date_range_start: Start date in ISO format (YYYY-MM-DD)
        date_range_end: End date in ISO format (YYYY-MM-DD)
        max_suggestions: Maximum number of suggestions to return
    
    Returns:
        List of optimal time slots with scores and reasoning
    """
    try:
        from datetime import datetime, timedelta
        
        # Parse date range (keep it simple with datetime)
        start_date = datetime.fromisoformat(date_range_start)
        end_date = datetime.fromisoformat(date_range_end)
        
        # Use existing scheduler engine (already returns formatted dictionaries)
        optimal_slots = find_optimal_meeting_slots(
            participants=participants,
            duration_minutes=duration_minutes,
            date_range_start=start_date,
            date_range_end=end_date
        )
        
        # Add timezone info and limit results
        formatted_slots = []
        for slot in optimal_slots[:max_suggestions]:
            slot_copy = slot.copy()
            slot_copy["timezone"] = "UTC"
            formatted_slots.append(slot_copy)
        
        return formatted_slots
        
    except Exception as e:
        logger.error(f"Error finding optimal slots: {e}")
        return [{
            "start_time": "",
            "end_time": "",
            "score": 0,
            "available_participants": [],
            "conflicted_participants": participants,
            "reasoning": f"Error: {str(e)}",
            "timezone": "UTC"
        }]

# AI Feature #5: Detect Scheduling Conflicts
@app.tool()
def detect_scheduling_conflicts(
    user_id: str,
    start_time: str,
    end_time: str
) -> List[Dict[str, Any]]:
    """
    Detect scheduling conflicts for a user in a given time range.
    
    Args:
        user_id: User ID or email to check conflicts for
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS)
        end_time: End time in ISO format (YYYY-MM-DDTHH:MM:SS)
    
    Returns:
        List of conflicting meetings with details and resolution suggestions
    """
    try:
        from datetime import datetime
        
        # Parse time range
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        
        # Use existing scheduler engine
        conflicts = detect_conflicts_engine(user_id, start_dt, end_dt)
        
        # Add resolution suggestions to each conflict
        enhanced_conflicts = []
        for conflict in conflicts:
            enhanced_conflict = conflict.copy()
            enhanced_conflict["resolution_suggestions"] = [
                "Move meeting to available time slot",
                "Reduce meeting duration",
                "Decline conflicting meeting if optional",
                "Delegate to team member if possible"
            ]
            enhanced_conflict["severity"] = "high" if conflict["conflict_type"] == "overlap" else "medium"
            enhanced_conflicts.append(enhanced_conflict)
        
        return enhanced_conflicts
        
    except Exception as e:
        logger.error(f"Error detecting conflicts: {e}")
        return [{
            "meeting_id": "error",
            "title": "Error detecting conflicts",
            "start_time": start_time,
            "end_time": end_time,
            "participants": [],
            "conflict_type": "system_error",
            "resolution_suggestions": ["Check system logs", "Verify user ID and time format"],
            "severity": "high"
        }]

# AI Feature #6: Generate Agenda Suggestions
@app.tool()
def generate_agenda_suggestions(
    meeting_title: str,
    participants: List[str],
    duration_minutes: int,
    meeting_type: str = "team_meeting",
    context: str = ""
) -> Dict[str, Any]:
    """
    Generate AI-powered agenda suggestions for a meeting.
    
    Args:
        meeting_title: Title of the meeting
        participants: List of participant emails
        duration_minutes: Meeting duration in minutes
        meeting_type: Type of meeting (team_meeting, 1:1, client_call, etc.)
        context: Additional context about the meeting
    
    Returns:
        Structured agenda with items, time allocations, and suggestions
    """
    try:
        import os
        import google.generativeai as genai
        
        # Initialize Gemini client (API key from environment)
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            # Return template agenda if no API key
            return _generate_template_agenda(meeting_title, participants, duration_minutes, meeting_type)
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Create context-aware prompt
        prompt = f"""
        Generate a structured agenda for a {meeting_type} meeting with the following details:
        
        Title: {meeting_title}
        Duration: {duration_minutes} minutes
        Participants: {len(participants)} people
        Type: {meeting_type}
        Context: {context if context else "No additional context provided"}
        
        Please provide:
        1. 3-5 main agenda items
        2. Time allocation for each item
        3. Meeting objectives
        4. Action items template
        5. Brief facilitation tips
        
        Format as JSON with this structure:
        {{
            "agenda_items": [
                {{"item": "item name", "duration": minutes, "description": "brief description"}}
            ],
            "objectives": ["objective 1", "objective 2"],
            "action_items_template": ["template item 1", "template item 2"],
            "facilitation_tips": ["tip 1", "tip 2"]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse AI response
        import json
        ai_response = response.text
        if not ai_response:
            raise ValueError("Empty response from Gemini")
        ai_agenda = json.loads(ai_response)
        
        # Add metadata
        ai_agenda["meeting_info"] = {
            "title": meeting_title,
            "duration_minutes": duration_minutes,
            "participant_count": len(participants),
            "meeting_type": meeting_type,
            "generated_by": "AI"
        }
        
        return ai_agenda
        
    except Exception as e:
        logger.error(f"Error generating agenda with AI: {e}")
        # Fallback to template agenda
        return _generate_template_agenda(meeting_title, participants, duration_minutes, meeting_type)

def _generate_template_agenda(title: str, participants: List[str], duration: int, meeting_type: str) -> Dict[str, Any]:
    """Generate a template agenda when AI is not available"""
    
    # Template agendas based on meeting type
    templates = {
        "team_meeting": {
            "agenda_items": [
                {"item": "Welcome & Check-in", "duration": 5, "description": "Quick team updates"},
                {"item": "Review Previous Action Items", "duration": 10, "description": "Progress on last meeting's tasks"},
                {"item": "Main Discussion", "duration": duration - 25, "description": "Core meeting topic"},
                {"item": "Next Steps & Action Items", "duration": 8, "description": "Assign tasks and deadlines"},
                {"item": "Wrap-up", "duration": 2, "description": "Quick summary and next meeting"}
            ],
            "objectives": ["Align team on priorities", "Address blockers", "Plan next steps"],
            "facilitation_tips": ["Keep discussions focused", "Ensure everyone participates", "Document decisions"]
        },
        "1:1": {
            "agenda_items": [
                {"item": "Personal Check-in", "duration": 5, "description": "How are things going?"},
                {"item": "Work Progress Review", "duration": duration - 20, "description": "Discuss current projects"},
                {"item": "Feedback & Development", "duration": 10, "description": "Growth opportunities"},
                {"item": "Next Steps", "duration": 5, "description": "Action items and goals"}
            ],
            "objectives": ["Support team member", "Remove blockers", "Provide feedback"],
            "facilitation_tips": ["Listen actively", "Ask open questions", "Be supportive"]
        },
        "client_call": {
            "agenda_items": [
                {"item": "Welcome & Introductions", "duration": 5, "description": "Set the tone"},
                {"item": "Project Status Update", "duration": 15, "description": "Share progress"},
                {"item": "Client Feedback & Questions", "duration": duration - 30, "description": "Address concerns"},
                {"item": "Next Steps & Timeline", "duration": 10, "description": "Plan forward"}
            ],
            "objectives": ["Update client on progress", "Address concerns", "Maintain relationship"],
            "facilitation_tips": ["Be prepared", "Listen to feedback", "Be solution-focused"]
        }
    }
    
    template = templates.get(meeting_type, templates["team_meeting"])
    
    return {
        **template,
        "action_items_template": [
            "Action item 1: [Description] - Owner: [Name] - Due: [Date]",
            "Action item 2: [Description] - Owner: [Name] - Due: [Date]"
        ],
        "meeting_info": {
            "title": title,
            "duration_minutes": duration,
            "participant_count": len(participants),
            "meeting_type": meeting_type,
            "generated_by": "Template"
        }
    }

# AI Feature #7: Calculate Workload Balance
@app.tool()
def calculate_workload_balance(
    team_members: List[str],
    date_range_start: str,
    date_range_end: str,
    target_hours_per_week: int = 10
) -> Dict[str, Any]:
    """
    Calculate meeting workload balance across team members.
    
    Args:
        team_members: List of team member emails
        date_range_start: Start date in ISO format (YYYY-MM-DD)
        date_range_end: End date in ISO format (YYYY-MM-DD)
        target_hours_per_week: Target meeting hours per person per week
    
    Returns:
        Workload analysis with balance scores and recommendations
    """
    try:
        from datetime import datetime, timedelta
        import statistics
        
        # Parse date range
        start_date = datetime.fromisoformat(date_range_start)
        end_date = datetime.fromisoformat(date_range_end)
        
        # Calculate workload for each team member
        workload_data = {}
        all_meeting_times = []
        
        for member in team_members:
            # Get meetings for this member
            with db_manager.get_session() as session:
                meeting_service = MeetingService()
                meetings = meeting_service.get_user_meetings_in_range(
                    member, start_date, end_date
                )
                
                # Calculate total meeting time
                total_minutes = sum(meeting.duration_minutes for meeting in meetings)
                total_hours = total_minutes / 60
                
                # Calculate metrics
                meeting_count = len(meetings)
                avg_meeting_duration = total_minutes / meeting_count if meeting_count > 0 else 0
                
                # Calculate weeks in range
                weeks = (end_date - start_date).days / 7
                hours_per_week = total_hours / weeks if weeks > 0 else 0
                
                workload_data[member] = {
                    "total_meetings": meeting_count,
                    "total_hours": round(total_hours, 2),
                    "hours_per_week": round(hours_per_week, 2),
                    "avg_meeting_duration": round(avg_meeting_duration, 2),
                    "utilization": round((hours_per_week / target_hours_per_week) * 100, 1) if target_hours_per_week > 0 else 0,
                    "status": "overloaded" if hours_per_week > target_hours_per_week * 1.2 else 
                             "balanced" if hours_per_week >= target_hours_per_week * 0.8 else "underutilized"
                }
                
                all_meeting_times.append(hours_per_week)
        
        # Calculate team balance metrics
        if all_meeting_times:
            avg_hours = statistics.mean(all_meeting_times)
            std_dev = statistics.stdev(all_meeting_times) if len(all_meeting_times) > 1 else 0
            balance_score = max(0, 100 - (std_dev / avg_hours * 100)) if avg_hours > 0 else 100
        else:
            avg_hours = 0
            std_dev = 0
            balance_score = 100
        
        # Generate recommendations
        recommendations = []
        overloaded_members = [m for m, data in workload_data.items() if data["status"] == "overloaded"]
        underutilized_members = [m for m, data in workload_data.items() if data["status"] == "underutilized"]
        
        if overloaded_members:
            recommendations.append(f"Consider redistributing meetings from {', '.join(overloaded_members[:2])}")
        if underutilized_members:
            recommendations.append(f"Consider involving {', '.join(underutilized_members[:2])} in more meetings")
        if balance_score < 70:
            recommendations.append("High workload imbalance detected - review meeting distribution")
        if avg_hours > target_hours_per_week * 1.5:
            recommendations.append("Team may be over-meeting - consider consolidating or reducing meetings")
        
        if not recommendations:
            recommendations.append("Team workload is well balanced")
        
        return {
            "team_summary": {
                "total_members": len(team_members),
                "avg_hours_per_week": round(avg_hours, 2),
                "balance_score": round(balance_score, 1),
                "target_hours_per_week": target_hours_per_week,
                "analysis_period": f"{date_range_start} to {date_range_end}"
            },
            "member_workloads": workload_data,
            "recommendations": recommendations,
            "balance_status": "excellent" if balance_score >= 90 else
                             "good" if balance_score >= 70 else
                             "needs_attention" if balance_score >= 50 else "poor"
        }
        
    except Exception as e:
        logger.error(f"Error calculating workload balance: {e}")
        return {
            "team_summary": {
                "total_members": len(team_members),
                "avg_hours_per_week": 0,
                "balance_score": 0,
                "target_hours_per_week": target_hours_per_week,
                "analysis_period": f"{date_range_start} to {date_range_end}"
            },
            "member_workloads": {},
            "recommendations": [f"Error calculating workload: {str(e)}"],
            "balance_status": "error"
        }

# AI Feature #8: Score Meeting Effectiveness
@app.tool()
def score_meeting_effectiveness(
    meeting_id: str,
    include_ai_analysis: bool = True
) -> Dict[str, Any]:
    """
    Score meeting effectiveness based on various criteria.
    
    Args:
        meeting_id: ID of the meeting to analyze
        include_ai_analysis: Whether to include AI-powered insights
    
    Returns:
        Meeting effectiveness score with detailed analysis and recommendations
    """
    try:
        # Get meeting details
        with db_manager.get_session() as session:
            meeting_service = MeetingService()
            meeting = meeting_service.get_meeting_by_id(meeting_id)
            
            if not meeting:
                raise ValueError(f"Meeting {meeting_id} not found")
            
            # Calculate base effectiveness score
            effectiveness_score = 0
            score_breakdown = {}
            
            # 1. Duration Score (30 points max)
            duration_score = _score_duration(meeting.duration_minutes, meeting.meeting_type)
            effectiveness_score += duration_score
            score_breakdown["duration"] = {
                "score": duration_score,
                "max_score": 30,
                "reasoning": _get_duration_reasoning(meeting.duration_minutes, meeting.meeting_type)
            }
            
            # 2. Participant Count Score (25 points max)
            participant_score = _score_participants(len(meeting.participants), meeting.meeting_type)
            effectiveness_score += participant_score
            score_breakdown["participants"] = {
                "score": participant_score,
                "max_score": 25,
                "reasoning": _get_participant_reasoning(len(meeting.participants), meeting.meeting_type)
            }
            
            # 3. Timing Score (20 points max)
            timing_score = _score_timing(meeting.start_time)
            effectiveness_score += timing_score
            score_breakdown["timing"] = {
                "score": timing_score,
                "max_score": 20,
                "reasoning": _get_timing_reasoning(meeting.start_time)
            }
            
            # 4. Agenda Score (15 points max)
            agenda_score = _score_agenda(meeting.agenda_items)
            effectiveness_score += agenda_score
            score_breakdown["agenda"] = {
                "score": agenda_score,
                "max_score": 15,
                "reasoning": _get_agenda_reasoning(meeting.agenda_items)
            }
            
            # 5. Follow-up Score (10 points max)
            followup_score = _score_followup(meeting.follow_up_actions)
            effectiveness_score += followup_score
            score_breakdown["followup"] = {
                "score": followup_score,
                "max_score": 10,
                "reasoning": _get_followup_reasoning(meeting.follow_up_actions)
            }
            
            # Generate recommendations
            recommendations = _generate_effectiveness_recommendations(meeting, score_breakdown)
            
            # Add AI analysis if requested
            ai_insights = []
            if include_ai_analysis:
                ai_insights = _generate_ai_insights(meeting, effectiveness_score)
            
            # Store insights in database
            insight_service = MeetingInsightService()
            insight_service.create_insight(
                meeting_id=meeting_id,
                effectiveness_score=effectiveness_score,
                insights=ai_insights if ai_insights else ["Effectiveness score calculated"],
                recommendations=recommendations,
                analysis_data=score_breakdown
            )
            
            return {
                "meeting_info": {
                    "id": meeting_id,
                    "title": meeting.title,
                    "duration": meeting.duration_minutes,
                    "participants": len(meeting.participants),
                    "type": meeting.meeting_type.value
                },
                "effectiveness_score": round(effectiveness_score, 1),
                "score_breakdown": score_breakdown,
                "grade": _get_effectiveness_grade(effectiveness_score),
                "recommendations": recommendations,
                "ai_insights": ai_insights,
                "analyzed_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error scoring meeting effectiveness: {e}")
        return {
            "meeting_info": {"id": meeting_id, "title": "Error", "duration": 0, "participants": 0, "type": "unknown"},
            "effectiveness_score": 0,
            "score_breakdown": {},
            "grade": "Error",
            "recommendations": [f"Error analyzing meeting: {str(e)}"],
            "ai_insights": [],
            "analyzed_at": datetime.now().isoformat()
        }

def _score_duration(duration: int, meeting_type: str) -> float:
    """Score meeting duration appropriateness"""
    optimal_durations = {
        "1:1": 30,
        "team_meeting": 45,
        "standup": 15,
        "all_hands": 60,
        "client_call": 45,
        "interview": 60,
        "brainstorm": 90,
        "review": 60
    }
    
    optimal = optimal_durations.get(meeting_type, 45)
    
    if duration <= optimal:
        return 30 * (duration / optimal)
    else:
        # Penalty for going over
        over_ratio = duration / optimal
        return max(0, 30 - ((over_ratio - 1) * 15))

def _score_participants(count: int, meeting_type: str) -> float:
    """Score participant count appropriateness"""
    optimal_counts = {
        "1:1": (2, 2),
        "team_meeting": (3, 8),
        "standup": (3, 10),
        "all_hands": (10, 50),
        "client_call": (2, 6),
        "interview": (2, 4),
        "brainstorm": (4, 8),
        "review": (2, 6)
    }
    
    min_count, max_count = optimal_counts.get(meeting_type, (3, 8))
    
    if min_count <= count <= max_count:
        return 25
    elif count < min_count:
        return max(0, 25 - (min_count - count) * 5)
    else:
        return max(0, 25 - (count - max_count) * 3)

def _score_timing(start_time: datetime) -> float:
    """Score meeting timing"""
    hour = start_time.hour
    
    if 9 <= hour <= 11:  # Peak productivity hours
        return 20
    elif 14 <= hour <= 16:  # Good afternoon slot
        return 15
    elif 8 <= hour <= 9 or 11 <= hour <= 14:  # Decent times
        return 10
    else:  # Early morning or late day
        return 5

def _score_agenda(agenda_items: List[str]) -> float:
    """Score agenda preparation"""
    if not agenda_items:
        return 0
    elif len(agenda_items) == 1:
        return 5
    elif 2 <= len(agenda_items) <= 5:
        return 15
    else:
        return 10  # Too many items

def _score_followup(follow_up_actions: List[str]) -> float:
    """Score follow-up actions"""
    if not follow_up_actions:
        return 0
    elif len(follow_up_actions) <= 3:
        return 10
    else:
        return 8  # Too many actions

def _get_duration_reasoning(duration: int, meeting_type: str) -> str:
    """Get reasoning for duration score"""
    if duration <= 15:
        return "Very short meeting - good for quick updates"
    elif duration <= 45:
        return "Appropriate duration for most meetings"
    elif duration <= 90:
        return "Longer meeting - ensure it's necessary"
    else:
        return "Very long meeting - consider breaking into smaller sessions"

def _get_participant_reasoning(count: int, meeting_type: str) -> str:
    """Get reasoning for participant score"""
    if count <= 2:
        return "Small group - good for focused discussions"
    elif count <= 6:
        return "Good size for productive discussions"
    elif count <= 10:
        return "Larger group - may need more structure"
    else:
        return "Very large group - consider if everyone needs to attend"

def _get_timing_reasoning(start_time: datetime) -> str:
    """Get reasoning for timing score"""
    hour = start_time.hour
    
    if 9 <= hour <= 11:
        return "Excellent timing - peak productivity hours"
    elif 14 <= hour <= 16:
        return "Good afternoon slot"
    elif hour < 8:
        return "Very early - may affect attendance"
    elif hour > 17:
        return "Late in day - people may be tired"
    else:
        return "Decent timing"

def _get_agenda_reasoning(agenda_items: List[str]) -> str:
    """Get reasoning for agenda score"""
    if not agenda_items:
        return "No agenda items - meetings are more effective with clear agendas"
    elif len(agenda_items) == 1:
        return "Single agenda item - consider adding more structure"
    elif 2 <= len(agenda_items) <= 5:
        return "Good agenda structure with clear items"
    else:
        return "Many agenda items - may be trying to cover too much"

def _get_followup_reasoning(follow_up_actions: List[str]) -> str:
    """Get reasoning for follow-up score"""
    if not follow_up_actions:
        return "No follow-up actions - consider what next steps are needed"
    elif len(follow_up_actions) <= 3:
        return "Good number of follow-up actions"
    else:
        return "Many follow-up actions - may be overwhelming"

def _generate_effectiveness_recommendations(meeting, score_breakdown: Dict) -> List[str]:
    """Generate recommendations based on scores"""
    recommendations = []
    
    if score_breakdown["duration"]["score"] < 20:
        recommendations.append("Consider optimizing meeting duration")
    if score_breakdown["participants"]["score"] < 15:
        recommendations.append("Review participant list - ensure all attendees are necessary")
    if score_breakdown["timing"]["score"] < 10:
        recommendations.append("Consider better timing for improved attendance and engagement")
    if score_breakdown["agenda"]["score"] < 10:
        recommendations.append("Prepare a detailed agenda with clear objectives")
    if score_breakdown["followup"]["score"] < 5:
        recommendations.append("Define clear action items and next steps")
    
    if not recommendations:
        recommendations.append("Meeting structure looks good - maintain current practices")
    
    return recommendations

def _generate_ai_insights(meeting, effectiveness_score: float) -> List[str]:
    """Generate AI insights if OpenAI is available"""
    try:
        import os
        import google.generativeai as genai
        
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        
        if not gemini_key:
            return ["AI insights require Gemini API key"]
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Analyze this meeting and provide 2-3 specific insights:
        
        Meeting: {meeting.title}
        Type: {meeting.meeting_type.value}
        Duration: {meeting.duration_minutes} minutes
        Participants: {len(meeting.participants)}
        Effectiveness Score: {effectiveness_score}/100
        
        Provide actionable insights to improve meeting effectiveness.
        """
        
        response = model.generate_content(prompt)
        
        ai_response = response.text
        if ai_response:
            return [insight.strip() for insight in ai_response.split('\n') if insight.strip()]
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        
    return ["AI insights temporarily unavailable"]

def _get_effectiveness_grade(score: float) -> str:
    """Convert score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

# AI Feature #9: Optimize Meeting Schedule (FINAL FEATURE!)
@app.tool()
def optimize_meeting_schedule(
    user_id: str,
    optimization_period_days: int = 14,
    include_ai_suggestions: bool = True
) -> Dict[str, Any]:
    """
    AI-powered comprehensive meeting schedule optimization.
    
    Args:
        user_id: User ID to optimize schedule for
        optimization_period_days: Number of days to analyze and optimize
        include_ai_suggestions: Whether to include AI-powered suggestions
    
    Returns:
        Comprehensive schedule optimization report with actionable recommendations
    """
    try:
        from datetime import datetime, timedelta
        
        # Define analysis period
        start_date = datetime.now()
        end_date = start_date + timedelta(days=optimization_period_days)
        
        # Get user's meetings in the period
        with db_manager.get_session() as session:
            meeting_service = MeetingService()
            user_meetings = meeting_service.get_user_meetings_in_range(
                user_id, start_date, end_date
            )
            
            if not user_meetings:
                return {
                    "user_id": user_id,
                    "analysis_period": f"{start_date.date()} to {end_date.date()}",
                    "optimization_score": 100,
                    "current_metrics": {"total_meetings": 0, "total_hours": 0},
                    "recommendations": ["No meetings found in the optimization period"],
                    "ai_suggestions": [],
                    "optimized_actions": []
                }
            
            # 1. Current Schedule Analysis
            current_metrics = _analyze_current_schedule(user_meetings)
            
            # 2. Conflict Analysis
            conflicts = []
            for meeting in user_meetings:
                meeting_conflicts = detect_conflicts_engine(
                    user_id, meeting.start_time, meeting.end_time
                )
                conflicts.extend(meeting_conflicts)
            
            # 3. Workload Analysis
            total_hours = sum(m.duration_minutes for m in user_meetings) / 60
            weeks = optimization_period_days / 7
            hours_per_week = total_hours / weeks if weeks > 0 else 0
            
            # 4. Meeting Effectiveness Analysis
            effectiveness_scores = []
            for meeting in user_meetings[:5]:  # Analyze top 5 meetings
                try:
                    # Calculate basic effectiveness score internally
                    duration_score = _score_duration(meeting.duration_minutes, meeting.meeting_type.value)
                    participant_score = _score_participants(len(meeting.participants), meeting.meeting_type.value) 
                    timing_score = _score_timing(meeting.start_time)
                    basic_score = duration_score + participant_score + timing_score
                    effectiveness_scores.append(basic_score)
                except:
                    pass
            
            avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 70
            
            # 5. Calculate Optimization Score
            optimization_score = _calculate_optimization_score(
                current_metrics, len(conflicts), hours_per_week, avg_effectiveness
            )
            
            # 6. Generate Recommendations
            recommendations = _generate_optimization_recommendations(
                current_metrics, conflicts, hours_per_week, avg_effectiveness, user_meetings
            )
            
            # 7. AI-Powered Suggestions
            ai_suggestions = []
            if include_ai_suggestions:
                ai_suggestions = _generate_ai_optimization_suggestions(
                    user_id, current_metrics, optimization_score
                )
            
            # 8. Optimized Actions
            optimized_actions = _generate_optimized_actions(user_meetings, conflicts)
            
            return {
                "user_id": user_id,
                "analysis_period": f"{start_date.date()} to {end_date.date()}",
                "optimization_score": round(optimization_score, 1),
                "current_metrics": current_metrics,
                "conflict_summary": {
                    "total_conflicts": len(conflicts),
                    "conflict_types": list(set(c.get("conflict_type", "") for c in conflicts))
                },
                "workload_analysis": {
                    "total_hours": round(total_hours, 1),
                    "hours_per_week": round(hours_per_week, 1),
                    "meeting_count": len(user_meetings),
                    "avg_effectiveness": round(avg_effectiveness, 1)
                },
                "recommendations": recommendations,
                "ai_suggestions": ai_suggestions,
                "optimized_actions": optimized_actions,
                "next_review_date": (datetime.now() + timedelta(days=7)).date().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error optimizing schedule: {e}")
        return {
            "user_id": user_id,
            "analysis_period": "Error",
            "optimization_score": 0,
            "current_metrics": {},
            "recommendations": [f"Error optimizing schedule: {str(e)}"],
            "ai_suggestions": [],
            "optimized_actions": []
        }

def _analyze_current_schedule(meetings) -> Dict[str, Any]:
    """Analyze current schedule metrics"""
    if not meetings:
        return {"total_meetings": 0, "total_hours": 0, "avg_duration": 0, "meeting_types": {}}
    
    total_minutes = sum(m.duration_minutes for m in meetings)
    meeting_types = {}
    
    for meeting in meetings:
        meeting_type = meeting.meeting_type.value
        meeting_types[meeting_type] = meeting_types.get(meeting_type, 0) + 1
    
    return {
        "total_meetings": len(meetings),
        "total_hours": round(total_minutes / 60, 2),
        "avg_duration": round(total_minutes / len(meetings), 1),
        "meeting_types": meeting_types,
        "busiest_day": _find_busiest_day(meetings)
    }

def _find_busiest_day(meetings) -> str:
    """Find the busiest day of the week"""
    day_counts = {}
    for meeting in meetings:
        day = meeting.start_time.strftime("%A")
        day_counts[day] = day_counts.get(day, 0) + 1
    
    if not day_counts:
        return "No data"
    
    busiest_day = max(day_counts.items(), key=lambda x: x[1])
    return f"{busiest_day[0]} ({busiest_day[1]} meetings)"

def _calculate_optimization_score(current_metrics, conflict_count, hours_per_week, avg_effectiveness) -> float:
    """Calculate overall optimization score (0-100)"""
    score = 100
    
    # Penalty for conflicts
    score -= conflict_count * 10
    
    # Penalty for overload (>15 hours/week)
    if hours_per_week > 15:
        score -= (hours_per_week - 15) * 2
    
    # Penalty for too many meetings (>20/week)
    meetings_per_week = current_metrics.get("total_meetings", 0) / 2  # Assuming 2-week period
    if meetings_per_week > 20:
        score -= (meetings_per_week - 20) * 1
    
    # Bonus for high effectiveness
    if avg_effectiveness > 80:
        score += 5
    elif avg_effectiveness < 60:
        score -= 10
    
    return max(0, min(100, score))

def _generate_optimization_recommendations(current_metrics, conflicts, hours_per_week, avg_effectiveness, meetings) -> List[str]:
    """Generate specific optimization recommendations"""
    recommendations = []
    
    # Conflict recommendations
    if len(conflicts) > 0:
        recommendations.append(f"Resolve {len(conflicts)} scheduling conflicts to improve efficiency")
    
    # Workload recommendations
    if hours_per_week > 15:
        recommendations.append("Consider reducing meeting load - currently exceeding 15 hours/week")
    elif hours_per_week < 5:
        recommendations.append("Meeting engagement is low - consider more collaborative sessions")
    
    # Effectiveness recommendations
    if avg_effectiveness < 70:
        recommendations.append("Focus on improving meeting effectiveness through better agendas and preparation")
    
    # Meeting distribution recommendations
    if current_metrics.get("total_meetings", 0) > 0:
        avg_duration = current_metrics.get("avg_duration", 0)
        if avg_duration > 60:
            recommendations.append("Consider shorter, more focused meetings - current average is long")
        elif avg_duration < 15:
            recommendations.append("Very short meetings - consider combining related topics")
    
    # Day distribution
    busiest_day = current_metrics.get("busiest_day", "")
    if "(" in busiest_day and busiest_day.split("(")[1].split(" ")[0].isdigit():
        meeting_count = int(busiest_day.split("(")[1].split(" ")[0])
        if meeting_count > 5:
            recommendations.append(f"Distribute meetings more evenly - {busiest_day} is overloaded")
    
    if not recommendations:
        recommendations.append("Schedule looks well optimized - maintain current practices")
    
    return recommendations

def _generate_ai_optimization_suggestions(user_id: str, current_metrics: Dict, optimization_score: float) -> List[str]:
    """Generate AI-powered optimization suggestions"""
    try:
        import os
        import google.generativeai as genai
        
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        
        if not gemini_key:
            return ["AI suggestions require Gemini API key - using template suggestions"]
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Provide 3-4 specific, actionable suggestions to optimize this user's meeting schedule:
        
        Current Metrics:
        - Total meetings: {current_metrics.get('total_meetings', 0)}
        - Total hours: {current_metrics.get('total_hours', 0)}
        - Average duration: {current_metrics.get('avg_duration', 0)} minutes
        - Optimization score: {optimization_score}/100
        - Busiest day: {current_metrics.get('busiest_day', 'Unknown')}
        
        Focus on practical, implementable suggestions for better productivity.
        """
        
        response = model.generate_content(prompt)
        
        ai_response = response.text
        if ai_response:
            suggestions = [s.strip() for s in ai_response.split('\n') if s.strip() and not s.strip().startswith('#')]
            return suggestions[:4]  # Limit to 4 suggestions
            
    except Exception as e:
        logger.error(f"Error generating AI suggestions: {e}")
    
    # Fallback suggestions
    return [
        "Block focus time between meetings for deep work",
        "Consider grouping similar meetings on the same day",
        "Schedule buffer time before important meetings",
        "Review recurring meetings for continued relevance"
    ]

def _generate_optimized_actions(meetings, conflicts) -> List[Dict[str, Any]]:
    """Generate specific optimized actions"""
    actions = []
    
    # Actions for conflicts
    for conflict in conflicts[:3]:  # Top 3 conflicts
        actions.append({
            "type": "resolve_conflict",
            "priority": "high",
            "description": f"Reschedule '{conflict.get('title', 'meeting')}' to avoid conflict",
            "meeting_id": conflict.get("meeting_id"),
            "estimated_time_savings": "15-30 minutes"
        })
    
    # Actions for long meetings
    long_meetings = [m for m in meetings if m.duration_minutes > 90]
    for meeting in long_meetings[:2]:  # Top 2 long meetings
        actions.append({
            "type": "optimize_duration",
            "priority": "medium",
            "description": f"Review '{meeting.title}' - consider breaking into shorter sessions",
            "meeting_id": meeting.id,
            "estimated_time_savings": f"{meeting.duration_minutes - 60} minutes"
        })
    
    # Actions for meeting distribution
    if len(meetings) > 10:
        actions.append({
            "type": "redistribute_meetings",
            "priority": "low",
            "description": "Consider spreading meetings more evenly across the week",
            "meeting_id": None,
            "estimated_time_savings": "Improved focus time"
        })
    
    return actions

if __name__ == "__main__":
    # This will be used for testing
    print("Smart Meeting Assistant MCP Server")
    print("Use: fastmcp run src/main.py") 