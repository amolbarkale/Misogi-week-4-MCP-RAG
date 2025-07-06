"""
Smart Meeting Assistant - Data Models

This module defines the database models using SQLModel for type safety and 
automatic validation. Each model represents a table in our SQLite database.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from pydantic import BaseModel, field_validator


class TimezoneEnum(str, Enum):
    """Common timezone enums for user preferences"""
    UTC = "UTC"
    US_EASTERN = "US/Eastern"
    US_CENTRAL = "US/Central"
    US_MOUNTAIN = "US/Mountain"
    US_PACIFIC = "US/Pacific"
    EUROPE_LONDON = "Europe/London"
    EUROPE_PARIS = "Europe/Paris"
    EUROPE_BERLIN = "Europe/Berlin"
    ASIA_TOKYO = "Asia/Tokyo"
    ASIA_SHANGHAI = "Asia/Shanghai"
    ASIA_KOLKATA = "Asia/Kolkata"


class MeetingStatus(str, Enum):
    """Meeting status options"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class MeetingType(str, Enum):
    """Meeting type categories"""
    ONE_ON_ONE = "1:1"
    TEAM_MEETING = "team_meeting"
    ALL_HANDS = "all_hands"
    CLIENT_CALL = "client_call"
    INTERVIEW = "interview"
    STANDUP = "standup"
    BRAINSTORM = "brainstorm"
    REVIEW = "review"


# Database Models (tables)
class User(SQLModel, table=True):
    """User model with timezone and preferences"""
    
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    timezone: TimezoneEnum = Field(default=TimezoneEnum.UTC)
    
    # JSON field for flexible preferences
    preferences: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    
    # Relationships
    # meetings: List["Meeting"] = Relationship(back_populates="organizer")


class Meeting(SQLModel, table=True):
    """Meeting model with participants and scheduling details"""
    
    id: str = Field(primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    
    # Scheduling
    start_time: datetime = Field(index=True)
    end_time: datetime = Field(index=True)
    duration_minutes: int = Field(ge=1, le=480)  # 1 minute to 8 hours
    
    # People
    organizer_id: str = Field(foreign_key="user.id")
    participants: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Categorization
    meeting_type: MeetingType = Field(default=MeetingType.TEAM_MEETING)
    status: MeetingStatus = Field(default=MeetingStatus.SCHEDULED)
    
    # Location/Platform
    location: Optional[str] = Field(default=None)
    meeting_url: Optional[str] = Field(default=None)
    
    # Recurring pattern (JSON for flexibility)
    recurring_pattern: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)
    
    # AI Analysis
    agenda_items: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    follow_up_actions: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Relationships
    # organizer: User = Relationship(back_populates="meetings")
    # insights: List["MeetingInsight"] = Relationship(back_populates="meeting")
    
    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        """Ensure end_time is after start_time"""
        if info.data and 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('End time must be after start time')
        return v


class MeetingInsight(SQLModel, table=True):
    """AI-generated insights and analysis for meetings"""
    
    id: str = Field(primary_key=True)
    meeting_id: str = Field(foreign_key="meeting.id", index=True)
    
    # Effectiveness scoring
    effectiveness_score: float = Field(ge=0, le=100)  # 0-100 scale
    
    # Analysis data
    analysis_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Insights and recommendations
    insights: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    recommendations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now)
    analysis_version: str = Field(default="1.0")
    
    # Relationships
    # meeting: Meeting = Relationship(back_populates="insights")


# API Models (for requests/responses)
class UserCreate(BaseModel):
    """Model for creating new users"""
    name: str
    email: str
    timezone: TimezoneEnum = TimezoneEnum.UTC
    preferences: Dict[str, Any] = {}


class UserResponse(BaseModel):
    """Model for user API responses"""
    id: str
    name: str
    email: str
    timezone: TimezoneEnum
    preferences: Dict[str, Any]
    created_at: datetime
    is_active: bool


class MeetingCreate(BaseModel):
    """Model for creating new meetings"""
    title: str
    description: Optional[str] = None
    start_time: datetime
    duration_minutes: int = Field(ge=15, le=480)  # 15 minutes to 8 hours
    participants: List[str]
    meeting_type: MeetingType = MeetingType.TEAM_MEETING
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    recurring_pattern: Optional[Dict[str, Any]] = None


class MeetingResponse(BaseModel):
    """Model for meeting API responses"""
    id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    organizer_id: str
    participants: List[str]
    meeting_type: MeetingType
    status: MeetingStatus
    location: Optional[str]
    meeting_url: Optional[str]
    agenda_items: List[str]
    created_at: datetime


class MeetingInsightResponse(BaseModel):
    """Model for meeting insight API responses"""
    id: str
    meeting_id: str
    effectiveness_score: float
    insights: List[str]
    recommendations: List[str]
    analyzed_at: datetime


class SchedulingPreferences(BaseModel):
    """Model for scheduling preferences"""
    preferred_start_time: Optional[str] = "09:00"  # HH:MM format
    preferred_end_time: Optional[str] = "17:00"    # HH:MM format
    min_break_minutes: int = 15
    max_daily_meetings: int = 8
    avoid_back_to_back: bool = True
    buffer_minutes: int = 5


class OptimalSlotRequest(BaseModel):
    """Request model for finding optimal meeting slots"""
    participants: List[str]
    duration_minutes: int
    date_range_start: datetime
    date_range_end: datetime
    preferences: Optional[SchedulingPreferences] = None


class OptimalSlotResponse(BaseModel):
    """Response model for optimal meeting slots"""
    start_time: datetime
    end_time: datetime
    score: float  # 0-100, higher is better
    participants_available: List[str]
    participants_conflicts: List[str]
    reasoning: str 