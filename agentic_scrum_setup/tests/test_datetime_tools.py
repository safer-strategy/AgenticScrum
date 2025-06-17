#!/usr/bin/env python3
"""Unit tests for DateTime MCP server functionality."""

import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the templates directory to Python path for testing
template_dir = Path(__file__).parent.parent / 'templates' / 'mcp_servers' / 'datetime'
sys.path.insert(0, str(template_dir))

from datetime_tools import DateTimeTools


class TestDateTimeTools(unittest.TestCase):
    """Test cases for DateTimeTools class."""

    def setUp(self):
        """Set up test fixtures."""
        self.dt_tools = DateTimeTools()

    def test_get_current_time_utc(self):
        """Test getting current time in UTC."""
        result = self.dt_tools.get_current_time()
        
        self.assertIsInstance(result, dict)
        self.assertIn('timestamp', result)
        self.assertIn('unix', result)
        self.assertIn('timezone', result)
        self.assertIn('components', result)
        
        # Check components structure
        components = result['components']
        self.assertIn('year', components)
        self.assertIn('month', components)
        self.assertIn('day', components)
        self.assertIn('hour', components)
        self.assertIn('minute', components)
        self.assertIn('second', components)
        self.assertIn('weekday', components)
        self.assertIn('week_number', components)

    def test_get_current_time_with_timezone(self):
        """Test getting current time with specific timezone."""
        result = self.dt_tools.get_current_time("US/Eastern")
        
        self.assertIsInstance(result, dict)
        self.assertIn('timezone', result)
        self.assertIn('US/Eastern', result['timezone'])

    def test_get_current_time_invalid_timezone(self):
        """Test getting current time with invalid timezone."""
        result = self.dt_tools.get_current_time("Invalid/Timezone")
        
        self.assertIn('error', result)

    def test_format_datetime_iso8601(self):
        """Test formatting datetime in ISO8601 format."""
        timestamp = "2025-01-18T10:30:00Z"
        result = self.dt_tools.format_datetime(timestamp, "ISO8601")
        
        self.assertIsInstance(result, str)
        self.assertIn("2025-01-18", result)

    def test_format_datetime_human(self):
        """Test formatting datetime in human-readable format."""
        timestamp = "2025-01-18T10:30:00Z"
        result = self.dt_tools.format_datetime(timestamp, "human")
        
        self.assertIsInstance(result, str)
        self.assertIn("January", result)
        self.assertIn("2025", result)

    def test_format_datetime_invalid(self):
        """Test formatting invalid datetime."""
        result = self.dt_tools.format_datetime("invalid-datetime", "ISO8601")
        
        self.assertIn("Error formatting datetime", result)

    def test_calculate_duration(self):
        """Test calculating duration between timestamps."""
        start = "2025-01-18T10:00:00Z"
        end = "2025-01-18T12:30:45Z"
        
        result = self.dt_tools.calculate_duration(start, end)
        
        self.assertIsInstance(result, dict)
        self.assertIn('total_seconds', result)
        self.assertIn('hours', result)
        self.assertIn('minutes', result)
        self.assertIn('human_readable', result)
        
        # Check calculated values
        self.assertEqual(result['hours'], 2)
        self.assertEqual(result['minutes'], 30)
        self.assertFalse(result['is_negative'])

    def test_calculate_duration_negative(self):
        """Test calculating negative duration."""
        start = "2025-01-18T12:00:00Z"
        end = "2025-01-18T10:00:00Z"
        
        result = self.dt_tools.calculate_duration(start, end)
        
        self.assertTrue(result['is_negative'])

    def test_calculate_duration_invalid(self):
        """Test calculating duration with invalid timestamps."""
        result = self.dt_tools.calculate_duration("invalid", "also-invalid")
        
        self.assertIn('error', result)

    def test_add_time_days(self):
        """Test adding days to timestamp."""
        timestamp = "2025-01-18T10:00:00Z"
        result = self.dt_tools.add_time(timestamp, days=5)
        
        self.assertIsInstance(result, str)
        self.assertIn("2025-01-23", result)

    def test_add_time_hours_minutes(self):
        """Test adding hours and minutes to timestamp."""
        timestamp = "2025-01-18T10:00:00Z"
        result = self.dt_tools.add_time(timestamp, hours=2, minutes=30)
        
        self.assertIn("12:30", result)

    def test_add_time_months(self):
        """Test adding months to timestamp."""
        timestamp = "2025-01-18T10:00:00Z"
        result = self.dt_tools.add_time(timestamp, months=2)
        
        self.assertIn("2025-03", result)

    def test_add_time_invalid(self):
        """Test adding time to invalid timestamp."""
        result = self.dt_tools.add_time("invalid-timestamp", days=1)
        
        self.assertIn("Error adding time", result)

    def test_convert_timezone(self):
        """Test timezone conversion."""
        timestamp = "2025-01-18T15:00:00Z"
        result = self.dt_tools.convert_timezone(timestamp, "UTC", "US/Eastern")
        
        self.assertIsInstance(result, str)
        # EST is UTC-5, so 15:00 UTC should be 10:00 EST
        self.assertIn("10:00", result)

    def test_convert_timezone_invalid(self):
        """Test timezone conversion with invalid timezone."""
        timestamp = "2025-01-18T15:00:00Z"
        result = self.dt_tools.convert_timezone(timestamp, "UTC", "Invalid/Timezone")
        
        self.assertIn("Error converting timezone", result)

    def test_calculate_business_days(self):
        """Test calculating business days."""
        # Monday to Friday (5 business days)
        start_date = "2025-01-20"  # Monday
        end_date = "2025-01-24"    # Friday
        
        result = self.dt_tools.calculate_business_days(start_date, end_date)
        
        self.assertIsInstance(result, dict)
        self.assertIn('business_days', result)
        self.assertIn('total_days', result)
        self.assertIn('weekend_days', result)
        
        self.assertEqual(result['business_days'], 5)
        self.assertEqual(result['total_days'], 5)
        self.assertEqual(result['weekend_days'], 0)

    def test_calculate_business_days_with_weekend(self):
        """Test calculating business days including weekend."""
        # Monday to Sunday (5 business days, 2 weekend days)
        start_date = "2025-01-20"  # Monday
        end_date = "2025-01-26"    # Sunday
        
        result = self.dt_tools.calculate_business_days(start_date, end_date)
        
        self.assertEqual(result['business_days'], 5)
        self.assertEqual(result['weekend_days'], 2)

    def test_calculate_business_days_with_holidays(self):
        """Test calculating business days with holidays."""
        start_date = "2025-01-20"  # Monday
        end_date = "2025-01-24"    # Friday
        holidays = ["2025-01-22"]  # Wednesday holiday
        
        result = self.dt_tools.calculate_business_days(start_date, end_date, holidays)
        
        self.assertEqual(result['business_days'], 4)  # 5 - 1 holiday
        self.assertEqual(result['holiday_count'], 1)

    def test_get_relative_time_past(self):
        """Test getting relative time for past timestamp."""
        # Mock current time
        with patch.object(self.dt_tools, '_format_past_time', return_value="2 hours ago"):
            past_time = "2025-01-18T08:00:00Z"
            result = self.dt_tools.get_relative_time(past_time, "2025-01-18T10:00:00Z")
            
            self.assertEqual(result, "2 hours ago")

    def test_get_relative_time_future(self):
        """Test getting relative time for future timestamp."""
        with patch.object(self.dt_tools, '_format_future_time', return_value="in 2 hours"):
            future_time = "2025-01-18T12:00:00Z"
            result = self.dt_tools.get_relative_time(future_time, "2025-01-18T10:00:00Z")
            
            self.assertEqual(result, "in 2 hours")

    def test_calculate_sprint_dates(self):
        """Test calculating sprint dates."""
        start_date = "2025-01-18"  # Saturday
        result = self.dt_tools.calculate_sprint_dates(start_date, 14)
        
        self.assertIsInstance(result, dict)
        self.assertIn('sprint_start', result)
        self.assertIn('sprint_end', result)
        self.assertIn('next_sprint_start', result)
        self.assertIn('working_days', result)
        
        # Sprint should start on Monday (2025-01-20)
        self.assertIn("2025-01-20", result['sprint_start'])

    def test_calculate_sprint_dates_monday_start(self):
        """Test calculating sprint dates when start is already Monday."""
        start_date = "2025-01-20"  # Monday
        result = self.dt_tools.calculate_sprint_dates(start_date, 14)
        
        # Should start on the same Monday
        self.assertEqual(result['sprint_start'], "2025-01-20")

    def test_get_time_until_future(self):
        """Test getting time until future timestamp."""
        current_time = "2025-01-18T10:00:00Z"
        target_time = "2025-01-18T12:30:00Z"
        
        result = self.dt_tools.get_time_until(target_time, current_time)
        
        self.assertIsInstance(result, dict)
        self.assertIn('is_past', result)
        self.assertIn('total_seconds', result)
        self.assertIn('hours', result)
        self.assertIn('minutes', result)
        
        self.assertFalse(result['is_past'])
        self.assertEqual(result['hours'], 2)
        self.assertEqual(result['minutes'], 30)

    def test_get_time_until_past(self):
        """Test getting time until past timestamp."""
        current_time = "2025-01-18T12:00:00Z"
        target_time = "2025-01-18T10:00:00Z"
        
        result = self.dt_tools.get_time_until(target_time, current_time)
        
        self.assertTrue(result['is_past'])
        self.assertIn('overdue_by', result)

    def test_humanize_duration_seconds(self):
        """Test humanizing duration in seconds."""
        duration = timedelta(seconds=30)
        result = self.dt_tools._humanize_duration(duration)
        
        self.assertEqual(result, "30 seconds")

    def test_humanize_duration_minutes(self):
        """Test humanizing duration in minutes."""
        duration = timedelta(minutes=5)
        result = self.dt_tools._humanize_duration(duration)
        
        self.assertEqual(result, "5 minutes")

    def test_humanize_duration_hours(self):
        """Test humanizing duration in hours."""
        duration = timedelta(hours=2, minutes=30)
        result = self.dt_tools._humanize_duration(duration)
        
        self.assertEqual(result, "2 hours and 30 minutes")

    def test_humanize_duration_days(self):
        """Test humanizing duration in days."""
        duration = timedelta(days=3, hours=2)
        result = self.dt_tools._humanize_duration(duration)
        
        self.assertEqual(result, "3 days and 2 hours")

    def test_count_weekend_days(self):
        """Test counting weekend days."""
        from datetime import date
        start_date = date(2025, 1, 20)  # Monday
        end_date = date(2025, 1, 26)    # Sunday
        
        result = self.dt_tools._count_weekend_days(start_date, end_date)
        
        self.assertEqual(result, 2)  # Saturday and Sunday

    def test_calculate_working_days(self):
        """Test calculating working days."""
        from datetime import date
        start_date = date(2025, 1, 20)  # Monday
        end_date = date(2025, 1, 26)    # Sunday
        
        result = self.dt_tools._calculate_working_days(start_date, end_date)
        
        self.assertEqual(result, 5)  # Monday through Friday


class TestDateTimeIntegration(unittest.TestCase):
    """Integration tests for datetime functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.dt_tools = DateTimeTools()

    def test_complete_sprint_workflow(self):
        """Test complete sprint planning workflow."""
        # Start sprint planning
        planning_start = self.dt_tools.get_current_time()
        
        # Calculate sprint dates
        sprint_dates = self.dt_tools.calculate_sprint_dates(
            planning_start["timestamp"], 
            14
        )
        
        # Verify sprint structure
        self.assertIn('sprint_start', sprint_dates)
        self.assertIn('sprint_end', sprint_dates)
        self.assertIn('working_days', sprint_dates)
        
        # Calculate time until sprint start
        time_until_sprint = self.dt_tools.get_time_until(
            sprint_dates['sprint_start'] + "T09:00:00Z"
        )
        
        # Should be a valid time calculation
        self.assertIn('is_past', time_until_sprint)

    def test_bug_tracking_workflow(self):
        """Test bug tracking and aging workflow."""
        # Create bug timestamp
        bug_created = "2025-01-15T09:00:00Z"
        current_time = "2025-01-18T15:00:00Z"
        
        # Calculate bug age
        bug_age = self.dt_tools.calculate_duration(bug_created, current_time)
        
        # Get relative time
        relative_age = self.dt_tools.get_relative_time(bug_created, current_time)
        
        # Verify calculations
        self.assertIsInstance(bug_age, dict)
        self.assertIsInstance(relative_age, str)
        self.assertTrue(bug_age['days'] >= 3)

    def test_timezone_conversion_workflow(self):
        """Test timezone conversion workflow."""
        # Meeting scheduled in UTC
        meeting_utc = "2025-01-20T15:00:00Z"
        
        # Convert to different timezones
        eastern = self.dt_tools.convert_timezone(meeting_utc, "UTC", "US/Eastern")
        pacific = self.dt_tools.convert_timezone(meeting_utc, "UTC", "US/Pacific")
        london = self.dt_tools.convert_timezone(meeting_utc, "UTC", "Europe/London")
        
        # All should be valid conversions
        self.assertIsInstance(eastern, str)
        self.assertIsInstance(pacific, str)
        self.assertIsInstance(london, str)
        
        # Eastern should be 5 hours behind UTC (10:00)
        self.assertIn("10:00", eastern)
        # Pacific should be 8 hours behind UTC (07:00)
        self.assertIn("07:00", pacific)


if __name__ == '__main__':
    unittest.main()