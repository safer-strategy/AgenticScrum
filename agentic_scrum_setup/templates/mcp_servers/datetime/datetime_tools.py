#!/usr/bin/env python3
"""Core datetime functionality for AgenticScrum MCP server."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
import calendar


class DateTimeTools:
    """Core datetime functionality for MCP server."""
    
    def __init__(self):
        """Initialize datetime tools."""
        self.default_timezone = timezone.utc
    
    def get_current_time(self, timezone_name: Optional[str] = None) -> Dict[str, Any]:
        """Get current time in specified timezone or UTC."""
        try:
            if timezone_name:
                tz = pytz.timezone(timezone_name)
            else:
                tz = self.default_timezone
            
            now = datetime.now(tz)
            return {
                "timestamp": now.isoformat(),
                "unix": int(now.timestamp()),
                "timezone": str(tz),
                "utc_offset": now.strftime("%z"),
                "components": {
                    "year": now.year,
                    "month": now.month,
                    "day": now.day,
                    "hour": now.hour,
                    "minute": now.minute,
                    "second": now.second,
                    "weekday": now.strftime("%A"),
                    "week_number": now.isocalendar()[1]
                }
            }
        except Exception as e:
            return {"error": f"Invalid timezone: {str(e)}"}
    
    def format_datetime(self, timestamp: str, format_type: str = "ISO8601") -> str:
        """Format datetime string in specified format."""
        try:
            dt = parser.parse(timestamp)
            formats = {
                "ISO8601": dt.isoformat(),
                "RFC3339": dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "human": dt.strftime("%B %d, %Y at %I:%M %p"),
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M:%S"),
                "date_human": dt.strftime("%B %d, %Y"),
                "time_human": dt.strftime("%I:%M %p"),
                "short": dt.strftime("%m/%d/%Y %H:%M"),
                "log": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "filename": dt.strftime("%Y%m%d_%H%M%S")
            }
            return formats.get(format_type, dt.strftime(format_type))
        except Exception as e:
            return f"Error formatting datetime: {str(e)}"
    
    def calculate_duration(self, start: str, end: str) -> Dict[str, Any]:
        """Calculate duration between two timestamps."""
        try:
            start_dt = parser.parse(start)
            end_dt = parser.parse(end)
            duration = end_dt - start_dt
            
            total_seconds = int(duration.total_seconds())
            days = duration.days
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            seconds = duration.seconds % 60
            
            return {
                "total_seconds": total_seconds,
                "total_minutes": total_seconds // 60,
                "total_hours": total_seconds // 3600,
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
                "human_readable": self._humanize_duration(duration),
                "is_negative": total_seconds < 0
            }
        except Exception as e:
            return {"error": f"Error calculating duration: {str(e)}"}
    
    def add_time(self, timestamp: str, **kwargs) -> str:
        """Add time to a timestamp (days, hours, minutes, etc)."""
        try:
            dt = parser.parse(timestamp)
            
            # Handle common time units
            if 'days' in kwargs:
                dt += timedelta(days=kwargs['days'])
            if 'hours' in kwargs:
                dt += timedelta(hours=kwargs['hours'])
            if 'minutes' in kwargs:
                dt += timedelta(minutes=kwargs['minutes'])
            if 'seconds' in kwargs:
                dt += timedelta(seconds=kwargs['seconds'])
            if 'weeks' in kwargs:
                dt += timedelta(weeks=kwargs['weeks'])
            
            # Handle months and years using relativedelta
            relativedelta_kwargs = {}
            if 'months' in kwargs:
                relativedelta_kwargs['months'] = kwargs['months']
            if 'years' in kwargs:
                relativedelta_kwargs['years'] = kwargs['years']
            
            if relativedelta_kwargs:
                dt += relativedelta(**relativedelta_kwargs)
            
            return dt.isoformat()
        except Exception as e:
            return f"Error adding time: {str(e)}"
    
    def convert_timezone(self, timestamp: str, from_tz: str, to_tz: str) -> str:
        """Convert timestamp from one timezone to another."""
        try:
            dt = parser.parse(timestamp)
            
            # If datetime is naive, assume it's in from_tz
            if dt.tzinfo is None:
                from_timezone = pytz.timezone(from_tz)
                dt = from_timezone.localize(dt)
            
            # Convert to target timezone
            to_timezone = pytz.timezone(to_tz)
            converted_dt = dt.astimezone(to_timezone)
            
            return converted_dt.isoformat()
        except Exception as e:
            return f"Error converting timezone: {str(e)}"
    
    def calculate_business_days(self, start_date: str, end_date: str, 
                              holidays: Optional[List[str]] = None) -> Dict[str, Any]:
        """Calculate business days between two dates, excluding weekends and holidays."""
        try:
            start_dt = parser.parse(start_date).date()
            end_dt = parser.parse(end_date).date()
            
            if holidays is None:
                holidays = []
            
            holiday_dates = [parser.parse(h).date() for h in holidays]
            
            business_days = 0
            current_date = start_dt
            
            while current_date <= end_dt:
                # Monday = 0, Sunday = 6
                if current_date.weekday() < 5 and current_date not in holiday_dates:
                    business_days += 1
                current_date += timedelta(days=1)
            
            return {
                "business_days": business_days,
                "total_days": (end_dt - start_dt).days + 1,
                "weekend_days": self._count_weekend_days(start_dt, end_dt),
                "holiday_count": len([h for h in holiday_dates if start_dt <= h <= end_dt])
            }
        except Exception as e:
            return {"error": f"Error calculating business days: {str(e)}"}
    
    def get_relative_time(self, timestamp: str, reference: Optional[str] = None) -> str:
        """Convert timestamp to human-readable relative time."""
        try:
            dt = parser.parse(timestamp)
            ref_dt = parser.parse(reference) if reference else datetime.now(timezone.utc)
            
            # Ensure both datetimes are timezone-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if ref_dt.tzinfo is None:
                ref_dt = ref_dt.replace(tzinfo=timezone.utc)
            
            diff = ref_dt - dt
            total_seconds = int(diff.total_seconds())
            
            if total_seconds < 0:
                return self._format_future_time(abs(total_seconds))
            else:
                return self._format_past_time(total_seconds)
        except Exception as e:
            return f"Error calculating relative time: {str(e)}"
    
    def calculate_sprint_dates(self, start_date: str, sprint_length_days: int = 14) -> Dict[str, str]:
        """Calculate sprint start and end dates."""
        try:
            start = parser.parse(start_date).date()
            
            # Find next Monday if not already Monday
            days_until_monday = (7 - start.weekday()) % 7
            if start.weekday() != 0:  # If not Monday
                sprint_start = start + timedelta(days=days_until_monday)
            else:
                sprint_start = start
            
            # Calculate sprint end (business days)
            sprint_end = sprint_start + timedelta(days=sprint_length_days - 1)
            
            # Next sprint starts after a weekend gap
            next_sprint_start = sprint_end + timedelta(days=3)
            if next_sprint_start.weekday() != 0:  # Ensure it's Monday
                days_to_monday = (7 - next_sprint_start.weekday()) % 7
                next_sprint_start += timedelta(days=days_to_monday)
            
            return {
                "sprint_start": sprint_start.isoformat(),
                "sprint_end": sprint_end.isoformat(),
                "next_sprint_start": next_sprint_start.isoformat(),
                "sprint_length": sprint_length_days,
                "working_days": self._calculate_working_days(sprint_start, sprint_end)
            }
        except Exception as e:
            return {"error": f"Error calculating sprint dates: {str(e)}"}
    
    def get_time_until(self, target_timestamp: str, reference: Optional[str] = None) -> Dict[str, Any]:
        """Calculate time remaining until target timestamp."""
        try:
            target_dt = parser.parse(target_timestamp)
            ref_dt = parser.parse(reference) if reference else datetime.now(timezone.utc)
            
            # Ensure both are timezone-aware
            if target_dt.tzinfo is None:
                target_dt = target_dt.replace(tzinfo=timezone.utc)
            if ref_dt.tzinfo is None:
                ref_dt = ref_dt.replace(tzinfo=timezone.utc)
            
            duration = target_dt - ref_dt
            total_seconds = int(duration.total_seconds())
            
            if total_seconds < 0:
                return {
                    "is_past": True,
                    "message": "Target time has already passed",
                    "overdue_by": self._humanize_duration(abs(duration))
                }
            
            return {
                "is_past": False,
                "total_seconds": total_seconds,
                "days": duration.days,
                "hours": duration.seconds // 3600,
                "minutes": (duration.seconds % 3600) // 60,
                "human_readable": self._humanize_duration(duration)
            }
        except Exception as e:
            return {"error": f"Error calculating time until: {str(e)}"}
    
    def _humanize_duration(self, duration: timedelta) -> str:
        """Convert timedelta to human-readable string."""
        total_seconds = int(abs(duration.total_seconds()))
        
        if total_seconds < 60:
            return f"{total_seconds} second{'s' if total_seconds != 1 else ''}"
        
        minutes = total_seconds // 60
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if hours < 24:
            if remaining_minutes > 0:
                return f"{hours} hour{'s' if hours != 1 else ''} and {remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}"
            return f"{hours} hour{'s' if hours != 1 else ''}"
        
        days = hours // 24
        remaining_hours = hours % 24
        if remaining_hours > 0:
            return f"{days} day{'s' if days != 1 else ''} and {remaining_hours} hour{'s' if remaining_hours != 1 else ''}"
        return f"{days} day{'s' if days != 1 else ''}"
    
    def _format_past_time(self, seconds: int) -> str:
        """Format past time in human-readable format."""
        if seconds < 60:
            return "just now"
        
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        
        days = hours // 24
        if days < 30:
            return f"{days} day{'s' if days != 1 else ''} ago"
        
        months = days // 30
        if months < 12:
            return f"{months} month{'s' if months != 1 else ''} ago"
        
        years = months // 12
        return f"{years} year{'s' if years != 1 else ''} ago"
    
    def _format_future_time(self, seconds: int) -> str:
        """Format future time in human-readable format."""
        if seconds < 60:
            return "in a few seconds"
        
        minutes = seconds // 60
        if minutes < 60:
            return f"in {minutes} minute{'s' if minutes != 1 else ''}"
        
        hours = minutes // 60
        if hours < 24:
            return f"in {hours} hour{'s' if hours != 1 else ''}"
        
        days = hours // 24
        if days < 30:
            return f"in {days} day{'s' if days != 1 else ''}"
        
        months = days // 30
        if months < 12:
            return f"in {months} month{'s' if months != 1 else ''}"
        
        years = months // 12
        return f"in {years} year{'s' if years != 1 else ''}"
    
    def _count_weekend_days(self, start_date, end_date) -> int:
        """Count weekend days between two dates."""
        weekend_days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() >= 5:  # Saturday = 5, Sunday = 6
                weekend_days += 1
            current += timedelta(days=1)
        return weekend_days
    
    def _calculate_working_days(self, start_date, end_date) -> int:
        """Calculate working days (excluding weekends) between two dates."""
        working_days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # Monday = 0 to Friday = 4
                working_days += 1
            current += timedelta(days=1)
        return working_days