"""
Smart Meeting Assistant - Scheduling Engine

This module contains the core scheduling logic including conflict detection,
optimal time slot finding, and intelligent meeting recommendations.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

import pendulum
from pendulum import DateTime

from .models import Meeting, User, MeetingType, SchedulingPreferences, OptimalSlotResponse
from .database import MeetingService, UserService


@dataclass
class TimeSlot:
    """Represents a potential meeting time slot"""
    start_time: DateTime
    end_time: DateTime
    score: float = 0.0
    available_participants: List[str] = None
    conflicted_participants: List[str] = None
    reasoning: str = ""
    
    def __post_init__(self):
        if self.available_participants is None:
            self.available_participants = []
        if self.conflicted_participants is None:
            self.conflicted_participants = []


@dataclass
class ConflictDetails:
    """Details about a scheduling conflict"""
    meeting_id: str
    title: str
    start_time: DateTime
    end_time: DateTime
    participants: List[str]
    conflict_type: str  # 'overlap', 'back_to_back', 'buffer_violation'


class SchedulingEngine:
    """Core scheduling engine with intelligent algorithms"""
    
    def __init__(self):
        self.meeting_service = MeetingService()
        self.user_service = UserService()
    
    def detect_conflicts(self, user_id: str, start_time: datetime, end_time: datetime) -> List[ConflictDetails]:
        """
        Detect scheduling conflicts for a user in a given time range.
        
        Args:
            user_id: User to check conflicts for
            start_time: Start of the time range
            end_time: End of the time range
            
        Returns:
            List of conflict details
        """
        conflicts = []
        
        # Get user's existing meetings in an extended range (for buffer checking)
        extended_start = start_time - timedelta(hours=2)
        extended_end = end_time + timedelta(hours=2)
        
        existing_meetings = self.meeting_service.get_user_meetings_in_range(
            user_id, extended_start, extended_end
        )
        
        # Convert to pendulum for easier timezone handling
        target_start = pendulum.instance(start_time)
        target_end = pendulum.instance(end_time)
        
        for meeting in existing_meetings:
            meeting_start = pendulum.instance(meeting.start_time)
            meeting_end = pendulum.instance(meeting.end_time)
            
            # Check for direct overlap
            if self._times_overlap(target_start, target_end, meeting_start, meeting_end):
                conflicts.append(ConflictDetails(
                    meeting_id=meeting.id,
                    title=meeting.title,
                    start_time=meeting_start,
                    end_time=meeting_end,
                    participants=meeting.participants,
                    conflict_type='overlap'
                ))
            
            # Check for back-to-back meetings (potential issue)
            elif self._is_back_to_back(target_start, target_end, meeting_start, meeting_end):
                conflicts.append(ConflictDetails(
                    meeting_id=meeting.id,
                    title=meeting.title,
                    start_time=meeting_start,
                    end_time=meeting_end,
                    participants=meeting.participants,
                    conflict_type='back_to_back'
                ))
            
            # Check for buffer violations (meetings too close)
            elif self._violates_buffer(target_start, target_end, meeting_start, meeting_end, minutes=15):
                conflicts.append(ConflictDetails(
                    meeting_id=meeting.id,
                    title=meeting.title,
                    start_time=meeting_start,
                    end_time=meeting_end,
                    participants=meeting.participants,
                    conflict_type='buffer_violation'
                ))
        
        return conflicts
    
    def find_optimal_slots(self, 
                          participants: List[str], 
                          duration_minutes: int,
                          date_range_start: datetime,
                          date_range_end: datetime,
                          preferences: Optional[SchedulingPreferences] = None) -> List[OptimalSlotResponse]:
        """
        Find optimal meeting slots for given participants.
        
        Args:
            participants: List of participant user IDs
            duration_minutes: Meeting duration in minutes
            date_range_start: Start of search range
            date_range_end: End of search range
            preferences: Optional scheduling preferences
            
        Returns:
            List of optimal slots sorted by score (best first)
        """
        if not preferences:
            preferences = SchedulingPreferences()
        
        # Generate potential time slots
        potential_slots = self._generate_time_slots(
            date_range_start, date_range_end, duration_minutes, preferences
        )
        
        # Score each slot
        scored_slots = []
        for slot in potential_slots:
            score_info = self._score_time_slot(slot, participants, preferences)
            
            if score_info['score'] > 0:  # Only include viable slots
                scored_slots.append(OptimalSlotResponse(
                    start_time=slot.start_time.naive,
                    end_time=slot.end_time.naive,
                    score=score_info['score'],
                    participants_available=score_info['available'],
                    participants_conflicts=score_info['conflicted'],
                    reasoning=score_info['reasoning']
                ))
        
        # Sort by score (highest first) and return top 10
        scored_slots.sort(key=lambda x: x.score, reverse=True)
        return scored_slots[:10]
    
    def _generate_time_slots(self, 
                           start_date: datetime, 
                           end_date: datetime, 
                           duration_minutes: int,
                           preferences: SchedulingPreferences) -> List[TimeSlot]:
        """Generate potential meeting time slots"""
        slots = []
        
        # Convert to pendulum for easier manipulation
        current = pendulum.instance(start_date)
        end = pendulum.instance(end_date)
        
        # Parse preferred times
        pref_start_hour, pref_start_minute = map(int, preferences.preferred_start_time.split(':'))
        pref_end_hour, pref_end_minute = map(int, preferences.preferred_end_time.split(':'))
        
        while current < end:
            # Skip weekends for now (can be made configurable)
            if current.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current = current.next(pendulum.MONDAY).at(pref_start_hour, pref_start_minute)
                continue
            
            # Generate slots for each day within preferred hours
            day_start = current.at(pref_start_hour, pref_start_minute)
            day_end = current.at(pref_end_hour, pref_end_minute)
            
            # Generate slots every 30 minutes during preferred hours
            slot_start = day_start
            while slot_start + timedelta(minutes=duration_minutes) <= day_end:
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                
                slots.append(TimeSlot(
                    start_time=slot_start,
                    end_time=slot_end
                ))
                
                # Move to next slot (30-minute intervals)
                slot_start = slot_start + timedelta(minutes=30)
            
            # Move to next day
            current = current.next(pendulum.MONDAY if current.weekday() == 4 else current.add(days=1))
        
        return slots
    
    def _score_time_slot(self, slot: TimeSlot, participants: List[str], preferences: SchedulingPreferences) -> Dict[str, Any]:
        """
        Score a time slot based on participant availability and preferences.
        
        Returns:
            Dict with score, available participants, conflicted participants, and reasoning
        """
        score = 100.0  # Start with perfect score
        available_participants = []
        conflicted_participants = []
        reasoning_parts = []
        
        # Check each participant's availability
        for participant_id in participants:
            conflicts = self.detect_conflicts(
                participant_id,
                slot.start_time.naive,
                slot.end_time.naive
            )
            
            if conflicts:
                conflicted_participants.append(participant_id)
                # Major penalty for conflicts
                conflict_penalty = len(conflicts) * 30
                score -= conflict_penalty
                reasoning_parts.append(f"Conflicts for {participant_id}: {len(conflicts)}")
            else:
                available_participants.append(participant_id)
        
        # Bonus for all participants available
        if len(available_participants) == len(participants):
            score += 20
            reasoning_parts.append("All participants available")
        
        # Score based on time of day preferences
        hour = slot.start_time.hour
        
        # Morning boost (9-11 AM)
        if 9 <= hour <= 11:
            score += 15
            reasoning_parts.append("Good morning time")
        
        # Afternoon penalty (1-2 PM - lunch time)
        elif 13 <= hour <= 14:
            score -= 10
            reasoning_parts.append("Lunch time penalty")
        
        # Late afternoon slight penalty (4-5 PM)
        elif 16 <= hour <= 17:
            score -= 5
            reasoning_parts.append("Late afternoon")
        
        # Early/late hours penalty
        elif hour < 8 or hour > 18:
            score -= 25
            reasoning_parts.append("Outside normal hours")
        
        # Day of week scoring
        weekday = slot.start_time.weekday()
        if weekday == 0:  # Monday
            score += 5
            reasoning_parts.append("Monday energy")
        elif weekday == 4:  # Friday
            score -= 5
            reasoning_parts.append("Friday afternoon")
        
        # Buffer time scoring
        # (This would check for adequate breaks between meetings)
        
        # Meeting duration scoring
        if slot.end_time.hour - slot.start_time.hour >= 2:
            score -= 10
            reasoning_parts.append("Long meeting")
        
        # Ensure score is not negative
        score = max(0, score)
        
        return {
            'score': score,
            'available': available_participants,
            'conflicted': conflicted_participants,
            'reasoning': '; '.join(reasoning_parts) if reasoning_parts else "Standard slot"
        }
    
    def _times_overlap(self, start1: DateTime, end1: DateTime, start2: DateTime, end2: DateTime) -> bool:
        """Check if two time ranges overlap"""
        return start1 < end2 and start2 < end1
    
    def _is_back_to_back(self, start1: DateTime, end1: DateTime, start2: DateTime, end2: DateTime) -> bool:
        """Check if meetings are back-to-back"""
        return end1 == start2 or end2 == start1
    
    def _violates_buffer(self, start1: DateTime, end1: DateTime, start2: DateTime, end2: DateTime, minutes: int = 15) -> bool:
        """Check if meetings violate buffer time"""
        buffer = timedelta(minutes=minutes)
        
        # Check if there's insufficient buffer between meetings
        if end1 <= start2:  # Meeting 1 ends before meeting 2 starts
            return (start2 - end1) < buffer
        elif end2 <= start1:  # Meeting 2 ends before meeting 1 starts
            return (start1 - end2) < buffer
        
        return False
    
    def get_meeting_density(self, user_id: str, date: datetime) -> Dict[str, Any]:
        """
        Calculate meeting density for a user on a specific date.
        
        Args:
            user_id: User to analyze
            date: Date to analyze
            
        Returns:
            Dictionary with density metrics
        """
        # Get meetings for the day
        day_start = pendulum.instance(date).start_of('day')
        day_end = pendulum.instance(date).end_of('day')
        
        meetings = self.meeting_service.get_user_meetings_in_range(
            user_id, day_start.naive, day_end.naive
        )
        
        if not meetings:
            return {
                'total_meetings': 0,
                'total_meeting_time': 0,
                'free_time': 480,  # 8 hours
                'density_score': 0,
                'recommendation': 'Good day to schedule meetings'
            }
        
        total_meeting_time = sum(meeting.duration_minutes for meeting in meetings)
        working_hours = 8 * 60  # 480 minutes
        free_time = working_hours - total_meeting_time
        density_score = (total_meeting_time / working_hours) * 100
        
        # Generate recommendation
        if density_score < 25:
            recommendation = "Light meeting day - good for scheduling"
        elif density_score < 50:
            recommendation = "Moderate meeting load - schedule with care"
        elif density_score < 75:
            recommendation = "Heavy meeting day - avoid non-essential meetings"
        else:
            recommendation = "Overloaded day - consider rescheduling"
        
        return {
            'total_meetings': len(meetings),
            'total_meeting_time': total_meeting_time,
            'free_time': free_time,
            'density_score': density_score,
            'recommendation': recommendation
        }
    
    def suggest_meeting_alternatives(self, original_start: datetime, duration_minutes: int, participants: List[str]) -> List[OptimalSlotResponse]:
        """
        Suggest alternative meeting times if the original time has conflicts.
        
        Args:
            original_start: Original proposed start time
            duration_minutes: Meeting duration
            participants: List of participant IDs
            
        Returns:
            List of alternative time slots
        """
        # Search for alternatives in the next 7 days
        search_start = original_start
        search_end = original_start + timedelta(days=7)
        
        alternatives = self.find_optimal_slots(
            participants=participants,
            duration_minutes=duration_minutes,
            date_range_start=search_start,
            date_range_end=search_end
        )
        
        # Filter out the original time if it's in the results
        original_end = original_start + timedelta(minutes=duration_minutes)
        alternatives = [
            alt for alt in alternatives
            if not (alt.start_time <= original_start < alt.end_time or 
                   alt.start_time < original_end <= alt.end_time)
        ]
        
        return alternatives[:5]  # Return top 5 alternatives


# Global scheduling engine instance
scheduling_engine = SchedulingEngine()


# Helper functions for easy import
def detect_scheduling_conflicts(user_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """Helper function to detect conflicts and return as dictionaries"""
    conflicts = scheduling_engine.detect_conflicts(user_id, start_time, end_time)
    return [
        {
            'meeting_id': c.meeting_id,
            'title': c.title,
            'start_time': c.start_time.isoformat(),
            'end_time': c.end_time.isoformat(),
            'participants': c.participants,
            'conflict_type': c.conflict_type
        }
        for c in conflicts
    ]


def find_optimal_meeting_slots(participants: List[str], duration_minutes: int, 
                             date_range_start: datetime, date_range_end: datetime) -> List[Dict[str, Any]]:
    """Helper function to find optimal slots and return as dictionaries"""
    slots = scheduling_engine.find_optimal_slots(
        participants, duration_minutes, date_range_start, date_range_end
    )
    return [
        {
            'start_time': slot.start_time.isoformat(),
            'end_time': slot.end_time.isoformat(),
            'score': slot.score,
            'participants_available': slot.participants_available,
            'participants_conflicts': slot.participants_conflicts,
            'reasoning': slot.reasoning
        }
        for slot in slots
    ]


# Export for easy import
__all__ = [
    'SchedulingEngine',
    'TimeSlot',
    'ConflictDetails',
    'scheduling_engine',
    'detect_scheduling_conflicts',
    'find_optimal_meeting_slots'
] 