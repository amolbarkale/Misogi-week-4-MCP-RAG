"""
Seed Data Generator for Smart Meeting Assistant

This script generates sample users and meetings for testing and development.
"""

from datetime import datetime, timedelta
from typing import List

from src.database import UserService, MeetingService, init_database, reset_database
from src.models import UserCreate, MeetingCreate, TimezoneEnum, MeetingType


def create_sample_users() -> List[str]:
    """Create sample users across different timezones"""
    users_data = [
        {
            "name": "John Smith",
            "email": "john.smith@company.com",
            "timezone": TimezoneEnum.US_EASTERN,
            "preferences": {
                "preferred_start_time": "09:00",
                "preferred_end_time": "17:00",
                "max_daily_meetings": 6
            }
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@company.com", 
            "timezone": TimezoneEnum.US_PACIFIC,
            "preferences": {
                "preferred_start_time": "08:30",
                "preferred_end_time": "16:30",
                "max_daily_meetings": 8
            }
        },
        {
            "name": "David Wilson",
            "email": "david.wilson@company.com",
            "timezone": TimezoneEnum.US_CENTRAL,
            "preferences": {
                "preferred_start_time": "09:30",
                "preferred_end_time": "17:30",
                "max_daily_meetings": 7
            }
        },
        {
            "name": "Emma Davis",
            "email": "emma.davis@company.com",
            "timezone": TimezoneEnum.EUROPE_LONDON,
            "preferences": {
                "preferred_start_time": "09:00",
                "preferred_end_time": "17:00",
                "max_daily_meetings": 5
            }
        },
        {
            "name": "Michael Brown",
            "email": "michael.brown@company.com",
            "timezone": TimezoneEnum.EUROPE_PARIS,
            "preferences": {
                "preferred_start_time": "10:00",
                "preferred_end_time": "18:00",
                "max_daily_meetings": 6
            }
        },
        {
            "name": "Lisa Garcia",
            "email": "lisa.garcia@company.com",
            "timezone": TimezoneEnum.ASIA_TOKYO,
            "preferences": {
                "preferred_start_time": "09:00",
                "preferred_end_time": "17:00",
                "max_daily_meetings": 4
            }
        },
        {
            "name": "Robert Martinez",
            "email": "robert.martinez@company.com",
            "timezone": TimezoneEnum.US_MOUNTAIN,
            "preferences": {
                "preferred_start_time": "08:00",
                "preferred_end_time": "16:00",
                "max_daily_meetings": 7
            }
        },
        {
            "name": "Anna Chen",
            "email": "anna.chen@company.com",
            "timezone": TimezoneEnum.ASIA_SHANGHAI,
            "preferences": {
                "preferred_start_time": "09:30",
                "preferred_end_time": "17:30",
                "max_daily_meetings": 5
            }
        }
    ]
    
    user_ids = []
    print("Creating sample users...")
    
    for user_data in users_data:
        try:
            # Try to create user - if it fails due to duplicate email, we'll handle it
            user_create = UserCreate(**user_data)
            user = UserService.create_user(user_create)
            user_ids.append(user.id)
            print(f"  ✅ Created user: {user.name} ({user.email}) - {user.timezone}")
        except Exception as e:
            # If creation fails (likely due to duplicate email), try to find existing user
            if "UNIQUE constraint failed" in str(e):
                try:
                    existing_user = UserService.get_user_by_email(user_data["email"])
                    if existing_user:
                        user_ids.append(existing_user.id)
                        print(f"  ♻️  User already exists: {user_data['name']} ({user_data['email']})")
                    else:
                        print(f"  ❌ Failed to create or find user {user_data['email']}")
                except Exception as find_error:
                    print(f"  ❌ Failed to create user {user_data['email']}: {find_error}")
            else:
                print(f"  ❌ Failed to create user {user_data['email']}: {e}")
            continue
    
    return user_ids


def create_sample_meetings(user_ids: List[str]) -> List[str]:
    """Create sample meetings with various patterns"""
    meeting_ids = []
    
    # Base date - start from today
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    meetings_data = [
        {
            "title": "Team Standup",
            "description": "Daily team standup meeting",
            "start_time": base_date,
            "duration_minutes": 30,
            "participants": user_ids[:4],
            "meeting_type": MeetingType.STANDUP,
            "location": "Conference Room A"
        },
        {
            "title": "Project Planning Session",
            "description": "Q1 project planning and roadmap discussion",
            "start_time": base_date.replace(hour=10, minute=30),
            "duration_minutes": 90,
            "participants": user_ids[:6],
            "meeting_type": MeetingType.TEAM_MEETING,
            "meeting_url": "https://meet.google.com/abc-def-ghi"
        },
        {
            "title": "1:1 with Manager",
            "description": "Weekly one-on-one meeting",
            "start_time": base_date.replace(hour=14, minute=0),
            "duration_minutes": 60,
            "participants": [user_ids[0], user_ids[1]],
            "meeting_type": MeetingType.ONE_ON_ONE,
            "location": "Manager's Office"
        },
        {
            "title": "Client Demo",
            "description": "Product demonstration for key client",
            "start_time": base_date.replace(hour=15, minute=30),
            "duration_minutes": 45,
            "participants": user_ids[:3],
            "meeting_type": MeetingType.CLIENT_CALL,
            "meeting_url": "https://zoom.us/j/123456789"
        },
        {
            "title": "All Hands Meeting",
            "description": "Monthly company all-hands meeting",
            "start_time": base_date + timedelta(days=1, hours=1),
            "duration_minutes": 60,
            "participants": user_ids,
            "meeting_type": MeetingType.ALL_HANDS,
            "location": "Main Auditorium"
        },
        {
            "title": "Design Review",
            "description": "Review of new feature designs",
            "start_time": base_date + timedelta(days=1, hours=3),
            "duration_minutes": 120,
            "participants": user_ids[2:6],
            "meeting_type": MeetingType.REVIEW,
            "meeting_url": "https://meet.google.com/xyz-abc-123"
        },
        {
            "title": "Brainstorming Session",
            "description": "Creative brainstorming for marketing campaign",
            "start_time": base_date + timedelta(days=2, hours=2),
            "duration_minutes": 90,
            "participants": user_ids[1:5],
            "meeting_type": MeetingType.BRAINSTORM,
            "location": "Creative Space"
        },
        {
            "title": "Technical Interview",
            "description": "Senior developer interview",
            "start_time": base_date + timedelta(days=2, hours=5),
            "duration_minutes": 60,
            "participants": user_ids[0:3],
            "meeting_type": MeetingType.INTERVIEW,
            "meeting_url": "https://meet.google.com/interview-123"
        },
        {
            "title": "Weekly Team Sync",
            "description": "Weekly team synchronization meeting",
            "start_time": base_date + timedelta(days=3, hours=1),
            "duration_minutes": 45,
            "participants": user_ids[:5],
            "meeting_type": MeetingType.TEAM_MEETING,
            "location": "Conference Room B"
        },
        {
            "title": "Sprint Retrospective",
            "description": "Sprint retrospective and planning",
            "start_time": base_date + timedelta(days=4, hours=2),
            "duration_minutes": 90,
            "participants": user_ids[1:7],
            "meeting_type": MeetingType.REVIEW,
            "meeting_url": "https://meet.google.com/retro-456"
        }
    ]
    
    print("\nCreating sample meetings...")
    
    for meeting_data in meetings_data:
        try:
            # Use the first participant as the organizer
            organizer_id = meeting_data["participants"][0]
            
            meeting_create = MeetingCreate(**meeting_data)
            meeting = MeetingService.create_meeting(meeting_create, organizer_id)
            meeting_ids.append(meeting.id)
            
            print(f"  ✅ Created meeting: {meeting.title}")
            print(f"     📅 {meeting.start_time.strftime('%Y-%m-%d %H:%M')} - {meeting.duration_minutes} mins")
            print(f"     👥 {len(meeting.participants)} participants")
        except Exception as e:
            print(f"  ❌ Failed to create meeting '{meeting_data['title']}': {e}")
            continue
    
    return meeting_ids


def create_conflicting_meetings(user_ids: List[str]) -> List[str]:
    """Create some intentionally conflicting meetings for testing conflict detection"""
    meeting_ids = []
    
    # Create meetings that will conflict with existing ones
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    conflicting_meetings = [
        {
            "title": "Overlapping Meeting",
            "description": "This meeting overlaps with Team Standup",
            "start_time": base_date.replace(minute=15),  # Overlaps with standup
            "duration_minutes": 30,
            "participants": [user_ids[0], user_ids[2]],
            "meeting_type": MeetingType.TEAM_MEETING
        },
        {
            "title": "Back-to-Back Meeting",
            "description": "Meeting right after another one",
            "start_time": base_date.replace(hour=10, minute=0),  # Right after standup
            "duration_minutes": 45,
            "participants": [user_ids[1], user_ids[3]],
            "meeting_type": MeetingType.ONE_ON_ONE
        }
    ]
    
    print("\nCreating conflicting meetings for testing...")
    
    for meeting_data in conflicting_meetings:
        organizer_id = meeting_data["participants"][0]
        meeting_create = MeetingCreate(**meeting_data)
        meeting = MeetingService.create_meeting(meeting_create, organizer_id)
        meeting_ids.append(meeting.id)
        print(f"  ⚠️  Created conflicting meeting: {meeting.title}")
    
    return meeting_ids


def test_database_operations(user_ids: List[str], meeting_ids: List[str]):
    """Test various database operations"""
    print("\n🧪 Testing Database Operations...")
    
    # Test user retrieval
    user = UserService.get_user_by_id(user_ids[0])
    if user:
        print(f"✅ Retrieved user: {user.name} ({user.email})")
    else:
        print("❌ Failed to retrieve user")
    
    # Test meeting retrieval
    meeting = MeetingService.get_meeting_by_id(meeting_ids[0])
    if meeting:
        print(f"✅ Retrieved meeting: {meeting.title}")
    else:
        print("❌ Failed to retrieve meeting")
    
    # Test user meetings retrieval
    user_meetings = MeetingService.get_meetings_by_user(user_ids[0])
    print(f"✅ User has {len(user_meetings)} meetings")
    
    # Test date range query
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=7)
    range_meetings = MeetingService.get_meetings_in_range(start_date, end_date)
    print(f"✅ Found {len(range_meetings)} meetings in next 7 days")
    
    # Test database health
    from src.database import check_database_health
    health = check_database_health()
    print(f"✅ Database health: {health['status']}")
    print(f"   📊 Users: {health['user_count']}, Meetings: {health['meeting_count']}")


def main():
    """Main function to seed the database"""
    print("🌱 Smart Meeting Assistant - Seed Data Generator")
    print("=" * 50)
    
    # Initialize database
    print("Initializing database...")
    init_database()
    
    # Check current database state
    from src.database import check_database_health
    health = check_database_health()
    print(f"\nCurrent database state:")
    print(f"  Users: {health['user_count']}")
    print(f"  Meetings: {health['meeting_count']}")
    
    # Option to reset database
    if health['user_count'] > 0 or health['meeting_count'] > 0:
        reset_choice = input("\nDatabase has existing data. Reset before seeding? (y/N): ").lower()
        if reset_choice == 'y':
            reset_database()
            print("Database reset complete!")
        else:
            print("Will merge with existing data (skip duplicates)")
    
    # Create sample data
    user_ids = create_sample_users()
    meeting_ids = create_sample_meetings(user_ids)
    conflict_ids = create_conflicting_meetings(user_ids)
    
    # Test operations
    test_database_operations(user_ids, meeting_ids)
    
    print("\n🎉 Seed data generation complete!")
    print(f"Created {len(user_ids)} users and {len(meeting_ids + conflict_ids)} meetings")
    print("\nYou can now test the MCP server with real data!")


if __name__ == "__main__":
    main() 