"""
Simple Seed Data Generator for Smart Meeting Assistant

This is a simplified version that reliably creates sample data for testing.
"""

from datetime import datetime, timedelta

from src.database import reset_database, init_database, check_database_health
from src.database import UserService, MeetingService
from src.models import UserCreate, MeetingCreate, TimezoneEnum, MeetingType


def create_seed_data():
    """Create seed data from scratch"""
    print("🌱 Smart Meeting Assistant - Simple Seed Data Generator")
    print("=" * 60)
    
    # Always reset for reliability
    print("Resetting database for clean start...")
    reset_database()
    print("✅ Database reset complete!")
    
    # Create users
    print("\nCreating sample users...")
    users_data = [
        ("John Smith", "john.smith@company.com", TimezoneEnum.US_EASTERN),
        ("Sarah Johnson", "sarah.johnson@company.com", TimezoneEnum.US_PACIFIC),
        ("David Wilson", "david.wilson@company.com", TimezoneEnum.US_CENTRAL),
        ("Emma Davis", "emma.davis@company.com", TimezoneEnum.EUROPE_LONDON),
        ("Michael Brown", "michael.brown@company.com", TimezoneEnum.EUROPE_PARIS),
        ("Lisa Garcia", "lisa.garcia@company.com", TimezoneEnum.ASIA_TOKYO),
        ("Robert Martinez", "robert.martinez@company.com", TimezoneEnum.US_MOUNTAIN),
        ("Anna Chen", "anna.chen@company.com", TimezoneEnum.ASIA_SHANGHAI),
    ]
    
    user_ids = []
    for name, email, timezone in users_data:
        user_create = UserCreate(
            name=name,
            email=email,
            timezone=timezone,
            preferences={
                "preferred_start_time": "09:00",
                "preferred_end_time": "17:00",
                "max_daily_meetings": 6
            }
        )
        user_id = UserService.create_user(user_create)
        user_ids.append(user_id)
        print(f"  ✅ Created: {name} ({timezone})")
    
    # Create meetings
    print(f"\nCreating sample meetings...")
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    meetings_data = [
        ("Team Standup", base_date, 30, user_ids[:4], MeetingType.STANDUP),
        ("Project Planning", base_date.replace(hour=10, minute=30), 90, user_ids[:6], MeetingType.TEAM_MEETING),
        ("1:1 with Manager", base_date.replace(hour=14), 60, user_ids[:2], MeetingType.ONE_ON_ONE),
        ("Client Demo", base_date.replace(hour=15, minute=30), 45, user_ids[:3], MeetingType.CLIENT_CALL),
        ("All Hands", base_date + timedelta(days=1, hours=1), 60, user_ids, MeetingType.ALL_HANDS),
        ("Design Review", base_date + timedelta(days=1, hours=3), 120, user_ids[2:6], MeetingType.REVIEW),
        ("Brainstorming", base_date + timedelta(days=2, hours=2), 90, user_ids[1:5], MeetingType.BRAINSTORM),
        ("Interview", base_date + timedelta(days=2, hours=5), 60, user_ids[:3], MeetingType.INTERVIEW),
        ("Team Sync", base_date + timedelta(days=3, hours=1), 45, user_ids[:5], MeetingType.TEAM_MEETING),
        ("Retrospective", base_date + timedelta(days=4, hours=2), 90, user_ids[1:7], MeetingType.REVIEW),
    ]
    
    meeting_ids = []
    for title, start_time, duration, participants, meeting_type in meetings_data:
        meeting_create = MeetingCreate(
            title=title,
            description=f"Sample meeting: {title}",
            start_time=start_time,
            duration_minutes=duration,
            participants=participants,
            meeting_type=meeting_type
        )
        meeting_id = MeetingService.create_meeting(meeting_create, participants[0])
        meeting_ids.append(meeting_id)
        print(f"  ✅ Created: {title} ({duration} mins, {len(participants)} participants)")
    
    # Create some conflicts for testing
    print(f"\nCreating conflicting meetings for testing...")
    
    conflict_meetings = [
        ("Overlapping Meeting", base_date.replace(minute=15), 30, user_ids[:2]),
        ("Back-to-Back Meeting", base_date.replace(hour=10), 45, user_ids[2:4]),
    ]
    
    for title, start_time, duration, participants in conflict_meetings:
        meeting_create = MeetingCreate(
            title=title,
            description=f"Conflicting meeting: {title}",
            start_time=start_time,
            duration_minutes=duration,
            participants=participants,
            meeting_type=MeetingType.TEAM_MEETING
        )
        meeting_id = MeetingService.create_meeting(meeting_create, participants[0])
        meeting_ids.append(meeting_id)
        print(f"  ⚠️  Created conflict: {title}")
    
    # Final summary
    print(f"\n🎉 Seed data creation complete!")
    health = check_database_health()
    print(f"📊 Database summary:")
    print(f"   Users: {health['user_count']}")
    print(f"   Meetings: {health['meeting_count']}")
    print(f"   Status: {health['status']}")
    
    print(f"\n✨ Ready to test the MCP server!")
    print(f"   Run: venv\\Scripts\\python -m fastmcp run src.main:app")
    
    return user_ids, meeting_ids


if __name__ == "__main__":
    create_seed_data() 