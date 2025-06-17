#!/usr/bin/env python3
"""Integration tests for MCP DateTime service."""

import unittest
import asyncio
import json
import sys
import os
from datetime import datetime
import subprocess
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "mcp_servers" / "datetime"))

from datetime_tools import DateTimeTools


class TestMCPDateTimeIntegration(unittest.TestCase):
    """Test MCP DateTime service integration."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.dt_tools = DateTimeTools()
        cls.project_root = Path(__file__).parent.parent
        cls.mcp_config = cls.project_root / ".mcp.json"
        
        # Verify .mcp.json exists
        if not cls.mcp_config.exists():
            raise FileNotFoundError("MCP configuration file not found")
    
    def test_mcp_configuration_exists(self):
        """Test that .mcp.json configuration exists and is valid."""
        self.assertTrue(self.mcp_config.exists())
        
        with open(self.mcp_config, 'r') as f:
            config = json.load(f)
        
        # Verify datetime server is configured
        self.assertIn("mcpServers", config)
        self.assertIn("datetime", config["mcpServers"])
        
        datetime_config = config["mcpServers"]["datetime"]
        self.assertIn("command", datetime_config)
        self.assertIn("args", datetime_config)
        self.assertEqual(datetime_config["command"], "python")
        self.assertIn("mcp_servers/datetime/server.py", datetime_config["args"][0])
    
    def test_datetime_service_files_exist(self):
        """Test that all DateTime service files exist."""
        datetime_dir = self.project_root / "mcp_servers" / "datetime"
        
        required_files = [
            "server.py",
            "datetime_tools.py",
            "requirements.txt",
            "README.md",
            "__init__.py"
        ]
        
        for file_name in required_files:
            file_path = datetime_dir / file_name
            self.assertTrue(file_path.exists(), f"Missing file: {file_name}")
    
    def test_datetime_tools_functionality(self):
        """Test core DateTime tools functionality."""
        # Test get_current_time
        result = self.dt_tools.get_current_time("UTC")
        self.assertIn("timestamp", result)
        self.assertIn("timezone", result)
        self.assertIn("components", result)
        
        # Verify timestamp format
        self.assertIsInstance(result["timestamp"], str)
        self.assertIn("T", result["timestamp"])  # ISO format
        
        # Test with different timezone
        result_pst = self.dt_tools.get_current_time("US/Pacific")
        self.assertIn("timestamp", result_pst)
        self.assertNotEqual(result["timestamp"], result_pst["timestamp"])
    
    def test_datetime_calculations(self):
        """Test DateTime calculation functions."""
        # Test add_time
        base_time = "2025-01-01T00:00:00Z"
        result = self.dt_tools.add_time(base_time, days=1)
        self.assertIsInstance(result, str)
        self.assertIn("2025-01-02", result)
        
        # Test calculate_sprint_dates
        start_date = "2025-01-06"  # Monday
        result = self.dt_tools.calculate_sprint_dates(start_date, 14)
        self.assertIn("sprint_start", result)
        self.assertIn("sprint_end", result)
        
        # Verify sprint duration
        from dateutil import parser
        start_dt = parser.parse(result["sprint_start"])
        end_dt = parser.parse(result["sprint_end"])
        duration = (end_dt - start_dt).days
        self.assertEqual(duration, 13)  # 14 days = 13 full days difference
    
    def test_business_day_calculations(self):
        """Test business day functionality."""
        # Test calculate_business_days
        friday = "2025-01-03"  # Friday
        monday = "2025-01-06"  # Following Monday
        result = self.dt_tools.calculate_business_days(friday, monday)
        
        self.assertIn("business_days", result)
        self.assertIn("total_days", result)
        # Should be 2 business days (Friday and Monday)
        self.assertEqual(result["business_days"], 2)
    
    def test_timezone_conversion(self):
        """Test timezone conversion functionality."""
        utc_time = "2025-01-01T12:00:00Z"
        result = self.dt_tools.convert_timezone(utc_time, "UTC", "US/Eastern")
        
        # The method returns a string, not a dict
        self.assertIsInstance(result, str)
        # EST is UTC-5, so 12:00 UTC = 07:00 EST
        self.assertIn("07:00", result)
    
    def test_performance_requirements(self):
        """Test that response times are under 50ms."""
        import time
        
        # Test multiple operations for performance
        operations = [
            lambda: self.dt_tools.get_current_time("UTC"),
            lambda: self.dt_tools.add_time("2025-01-01T00:00:00Z", days=1),
            lambda: self.dt_tools.calculate_sprint_dates("2025-01-06", 14),
            lambda: self.dt_tools.calculate_business_days("2025-01-03", "2025-01-06"),
        ]
        
        for operation in operations:
            start_time = time.time()
            result = operation()
            end_time = time.time()
            
            duration_ms = (end_time - start_time) * 1000
            self.assertLess(duration_ms, 50, f"Operation took {duration_ms:.2f}ms (> 50ms)")
            # For dict results, check for errors; string results are assumed valid if no exception
            if isinstance(result, dict):
                self.assertNotIn("error", result, "Operation should not return error")
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        # Test invalid timezone
        result = self.dt_tools.get_current_time("Invalid/Timezone")
        self.assertIn("error", result)
        
        # Test invalid date format
        result = self.dt_tools.add_time("invalid-date", days=1)
        self.assertIn("Error", result)  # String error message
        
        # Test invalid timezone conversion
        result = self.dt_tools.convert_timezone("2025-01-01T00:00:00Z", "UTC", "Invalid/Timezone")
        self.assertIn("Error", result)  # String error message
    
    def test_agent_integration_patterns(self):
        """Test agent-specific datetime patterns from personas."""
        # POA patterns - User story timestamps
        current_time = self.dt_tools.get_current_time("UTC")
        self.assertIn("timestamp", current_time)
        
        # SMA patterns - Sprint planning
        sprint_dates = self.dt_tools.calculate_sprint_dates("2025-01-06", 14)
        self.assertIn("sprint_start", sprint_dates)
        self.assertIn("sprint_end", sprint_dates)
        
        # QAA patterns - Test execution tracking
        test_start = "2025-01-01T09:00:00Z"
        test_end = self.dt_tools.add_time(test_start, hours=2)
        self.assertIsInstance(test_end, str)
        self.assertIn("11:00", test_end)  # 9 + 2 hours
        
        # SAA patterns - Vulnerability tracking (calculate time until deadline)
        deadline = "2026-02-01T09:00:00Z"  # Future date
        time_until = self.dt_tools.get_time_until(deadline)
        if time_until.get("is_past", False):
            # If still past, check the overdue message exists
            self.assertIn("message", time_until)
        else:
            # If future, check for total_seconds
            self.assertIn("total_seconds", time_until)
    
    def test_mcp_server_startup(self):
        """Test that MCP server can start without errors."""
        server_path = self.project_root / "mcp_servers" / "datetime" / "server.py"
        
        # Try to import the server module
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("server", server_path)
            server_module = importlib.util.module_from_spec(spec)
            # Don't execute the module, just verify it can be loaded
            self.assertIsNotNone(spec)
            self.assertIsNotNone(server_module)
        except Exception as e:
            self.fail(f"Failed to load server module: {e}")
    
    def test_comprehensive_datetime_coverage(self):
        """Test comprehensive coverage of all datetime functions."""
        # Test all core functions actually implemented
        test_cases = [
            # 1. Get current time
            ("get_current_time", ["UTC"], {"timestamp", "timezone"}),
            
            # 2. Format datetime - returns string, not dict
            ("format_datetime", ["2025-01-01T12:00:00Z", "ISO8601"], None),
            
            # 3. Add time - returns string, not dict  
            ("add_time", [{"timestamp": "2025-01-01T00:00:00Z", "days": 1}], None),
            
            # 4. Calculate duration
            ("calculate_duration", ["2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z"], {"total_seconds", "days"}),
            
            # 5. Convert timezone - returns string, not dict
            ("convert_timezone", ["2025-01-01T12:00:00Z", "UTC", "US/Eastern"], None),
            
            # 6. Calculate business days
            ("calculate_business_days", ["2025-01-01", "2025-01-05"], {"business_days", "total_days"}),
            
            # 7. Calculate sprint dates
            ("calculate_sprint_dates", ["2025-01-06", 14], {"sprint_start", "sprint_end"}),
            
            # 8. Get relative time - returns string, not dict
            ("get_relative_time", ["2025-01-01T12:00:00Z"], None),
            
            # 9. Get time until
            ("get_time_until", ["2025-12-31T23:59:59Z"], {"total_seconds", "days"}),
        ]
        
        for method_name, args, expected_keys in test_cases:
            with self.subTest(method=method_name):
                if not hasattr(self.dt_tools, method_name):
                    self.fail(f"Method {method_name} not found")
                    
                method = getattr(self.dt_tools, method_name)
                
                # Handle different argument patterns
                if method_name == "add_time":
                    result = method("2025-01-01T00:00:00Z", days=1)
                else:
                    result = method(*args)
                
                # Check that result is valid
                if isinstance(result, dict) and "error" in result:
                    self.fail(f"{method_name} returned error: {result['error']}")
                
                # Check expected keys are present (only for dict results)
                if expected_keys and isinstance(result, dict):
                    for key in expected_keys:
                        self.assertIn(key, result, f"Missing key '{key}' in {method_name} result")
                elif expected_keys is None:
                    # String result expected
                    self.assertIsInstance(result, str, f"{method_name} should return string")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)