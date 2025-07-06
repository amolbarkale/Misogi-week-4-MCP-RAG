"""
Smart Meeting Assistant - Database Layer

This module handles SQLite database connection, table creation, and provides
CRUD operations for all models. Uses SQLModel for type-safe database operations.
"""

import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime, timedelta

from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy import event

from .models import User, Meeting, MeetingInsight, UserCreate, MeetingCreate, MeetingStatus


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, database_url: str = "sqlite:///./meetings.db"):
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL query logging
            connect_args={"check_same_thread": False}  # Needed for SQLite
        )
        
        # Enable foreign key constraints for SQLite
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            if 'sqlite' in database_url.lower():
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
    
    def create_tables(self):
        """Create all database tables"""
        SQLModel.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all database tables (for testing/reset)"""
        SQLModel.metadata.drop_all(self.engine)
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()


# User CRUD Operations
class UserService:
    """Service for user-related database operations"""
    
    @staticmethod
    def create_user(user_data: UserCreate) -> str:
        """Create a new user and return the user ID"""
        with db_manager.get_session() as session:
            # Generate unique ID
            user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            user = User(
                id=user_id,
                name=user_data.name,
                email=user_data.email,
                timezone=user_data.timezone,
                preferences=user_data.preferences
            )
            
            session.add(user)
            session.commit()
            # Return just the ID to avoid detached instance issues
            return user_id
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        with db_manager.get_session() as session:
            return session.get(User, user_id)
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        with db_manager.get_session() as session:
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()
            if user:
                # Refresh to ensure all attributes are loaded
                session.refresh(user)
            return user
    
    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users"""
        with db_manager.get_session() as session:
            statement = select(User).where(User.is_active == True)
            return session.exec(statement).all()
    
    @staticmethod
    def update_user_preferences(user_id: str, preferences: Dict[str, Any]) -> Optional[User]:
        """Update user preferences"""
        with db_manager.get_session() as session:
            user = session.get(User, user_id)
            if user:
                user.preferences = preferences
                user.updated_at = datetime.now()
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
    
    @staticmethod
    def deactivate_user(user_id: str) -> bool:
        """Deactivate user (soft delete)"""
        with db_manager.get_session() as session:
            user = session.get(User, user_id)
            if user:
                user.is_active = False
                user.updated_at = datetime.now()
                session.add(user)
                session.commit()
                return True
            return False


# Meeting CRUD Operations
class MeetingService:
    """Service for meeting-related database operations"""
    
    @staticmethod
    def create_meeting(meeting_data: MeetingCreate, organizer_email: str) -> str:
        """Create a new meeting"""
        with db_manager.get_session() as session:
            # Generate unique ID
            meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Look up organizer user ID from email within the same session
            from sqlmodel import select
            organizer_statement = select(User).where(User.email == organizer_email)
            organizer_user = session.exec(organizer_statement).first()
            
            if not organizer_user:
                raise ValueError(f"Organizer user not found: {organizer_email}")
            
            # Calculate end time using timedelta
            end_time = meeting_data.start_time + timedelta(minutes=meeting_data.duration_minutes)
            
            meeting = Meeting(
                id=meeting_id,
                title=meeting_data.title,
                description=meeting_data.description,
                start_time=meeting_data.start_time,
                end_time=end_time,
                duration_minutes=meeting_data.duration_minutes,
                organizer_id=organizer_user.id,  # Use user ID, not email
                participants=meeting_data.participants,
                meeting_type=meeting_data.meeting_type,
                location=meeting_data.location,
                meeting_url=meeting_data.meeting_url,
                recurring_pattern=meeting_data.recurring_pattern
            )
            
            session.add(meeting)
            session.commit()
            # Return just the ID to avoid detached instance issues
            return meeting_id
    
    @staticmethod
    def get_meeting_by_id(meeting_id: str) -> Optional[Meeting]:
        """Get meeting by ID"""
        with db_manager.get_session() as session:
            return session.get(Meeting, meeting_id)
    
    @staticmethod
    def get_meetings_by_user(user_id: str) -> List[Meeting]:
        """Get all meetings for a user (as organizer or participant)"""
        with db_manager.get_session() as session:
            # Get meetings where user is organizer
            organizer_statement = select(Meeting).where(Meeting.organizer_id == user_id)
            organizer_meetings = session.exec(organizer_statement).all()
            
            # Get meetings where user is participant (JSON search)
            participant_statement = select(Meeting).where(Meeting.participants.contains(user_id))
            participant_meetings = session.exec(participant_statement).all()
            
            # Combine and deduplicate
            all_meetings = list(set(organizer_meetings + participant_meetings))
            return sorted(all_meetings, key=lambda m: m.start_time)
    
    @staticmethod
    def get_meetings_in_range(start_date: datetime, end_date: datetime) -> List[Meeting]:
        """Get meetings within a date range"""
        with db_manager.get_session() as session:
            statement = select(Meeting).where(
                Meeting.start_time >= start_date,
                Meeting.start_time <= end_date
            )
            return session.exec(statement).all()
    
    @staticmethod
    def get_user_meetings_in_range(user_id: str, start_date: datetime, end_date: datetime) -> List[Meeting]:
        """Get user's meetings within a date range"""
        with db_manager.get_session() as session:
            # Organizer meetings
            organizer_statement = select(Meeting).where(
                Meeting.organizer_id == user_id,
                Meeting.start_time >= start_date,
                Meeting.start_time <= end_date
            )
            organizer_meetings = session.exec(organizer_statement).all()
            
            # Participant meetings
            participant_statement = select(Meeting).where(
                Meeting.participants.contains(user_id),
                Meeting.start_time >= start_date,
                Meeting.start_time <= end_date
            )
            participant_meetings = session.exec(participant_statement).all()
            
            # Combine and deduplicate
            all_meetings = list(set(organizer_meetings + participant_meetings))
            return sorted(all_meetings, key=lambda m: m.start_time)
    
    @staticmethod
    def update_meeting_status(meeting_id: str, status: str) -> Optional[Meeting]:
        """Update meeting status"""
        with db_manager.get_session() as session:
            meeting = session.get(Meeting, meeting_id)
            if meeting:
                meeting.status = status
                meeting.updated_at = datetime.now()
                session.add(meeting)
                session.commit()
                session.refresh(meeting)
            return meeting
    
    @staticmethod
    def delete_meeting(meeting_id: str) -> bool:
        """Delete meeting"""
        with db_manager.get_session() as session:
            meeting = session.get(Meeting, meeting_id)
            if meeting:
                session.delete(meeting)
                session.commit()
                return True
            return False


# Meeting Insight CRUD Operations
class MeetingInsightService:
    """Service for meeting insight operations"""
    
    @staticmethod
    def create_insight(meeting_id: str, effectiveness_score: float, 
                      insights: List[str], recommendations: List[str],
                      analysis_data: Dict[str, Any] = None) -> MeetingInsight:
        """Create meeting insight"""
        with db_manager.get_session() as session:
            insight_id = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            insight = MeetingInsight(
                id=insight_id,
                meeting_id=meeting_id,
                effectiveness_score=effectiveness_score,
                insights=insights,
                recommendations=recommendations,
                analysis_data=analysis_data or {}
            )
            
            session.add(insight)
            session.commit()
            session.refresh(insight)
            return insight
    
    @staticmethod
    def get_insight_by_meeting(meeting_id: str) -> Optional[MeetingInsight]:
        """Get insight for a meeting"""
        with db_manager.get_session() as session:
            statement = select(MeetingInsight).where(MeetingInsight.meeting_id == meeting_id)
            return session.exec(statement).first()
    
    @staticmethod
    def get_insights_by_user(user_id: str) -> List[MeetingInsight]:
        """Get all insights for meetings organized by user"""
        with db_manager.get_session() as session:
            statement = select(MeetingInsight).join(Meeting).where(Meeting.organizer_id == user_id)
            return session.exec(statement).all()


# Database initialization
def init_database():
    """Initialize database and create tables"""
    print("Initializing database...")
    db_manager.create_tables()
    print("Database initialized successfully!")


def reset_database():
    """Reset database (drop and recreate tables)"""
    print("Resetting database...")
    db_manager.drop_tables()
    db_manager.create_tables()
    print("Database reset successfully!")


# Health check functions
def check_database_health() -> Dict[str, Any]:
    """Check database connection and health"""
    try:
        with db_manager.get_session() as session:
            # Try to query a simple count
            user_count = len(session.exec(select(User)).all())
            meeting_count = len(session.exec(select(Meeting)).all())
            
            return {
                "status": "healthy",
                "database_url": db_manager.database_url,
                "user_count": user_count,
                "meeting_count": meeting_count,
                "tables_exist": True
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url": db_manager.database_url
        }


# Export services for easy import
__all__ = [
    "db_manager",
    "UserService", 
    "MeetingService",
    "MeetingInsightService",
    "init_database",
    "reset_database",
    "check_database_health"
] 