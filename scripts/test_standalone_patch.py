#!/usr/bin/env python3
"""Test script for verifying standalone agentic-patch operations."""

import subprocess
import sys
from pathlib import Path

def test_help():
    """Test help output shows all operations."""
    print("Testing help output...")
    result = subprocess.run([sys.executable, 'agentic-patch', '--help'], 
                          capture_output=True, text=True)
    
    # Check for new operations in help
    required_operations = ['update-all', 'add-background-agents', 'update-security']
    missing = []
    
    for op in required_operations:
        if op not in result.stdout:
            missing.append(op)
    
    if missing:
        print(f"❌ Missing operations in help: {missing}")
        print("Help output:")
        print(result.stdout)
        return False
    else:
        print("✅ All operations present in help")
        return True

def test_status():
    """Test status command works."""
    print("\nTesting status command...")
    result = subprocess.run([sys.executable, 'agentic-patch', 'status'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Status command failed: {result.stderr}")
        return False
    else:
        print("✅ Status command works")
        return True

def test_dry_run():
    """Test dry run for new operations."""
    print("\nTesting dry run operations...")
    
    # Test update-all dry run
    result = subprocess.run([sys.executable, 'agentic-patch', 'update-all', '--dry-run'], 
                          capture_output=True, text=True, cwd='/tmp')
    
    if result.returncode != 0:
        print(f"❌ update-all dry run failed: {result.stderr}")
        return False
    else:
        print("✅ update-all dry run works")
    
    return True

def main():
    """Run all tests."""
    script_dir = Path(__file__).parent
    
    # Change to scripts directory
    import os
    os.chdir(script_dir)
    
    print("🧪 Testing standalone agentic-patch script...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    tests = [
        test_help,
        test_status,
        test_dry_run
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} raised exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)