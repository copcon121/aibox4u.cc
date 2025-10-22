#!/usr/bin/env python3
"""
Unit tests for sync_tools_playwright.py
Tests the changes made to fix scraping issues
"""
import unittest
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestSyncToolsPlaywrightChanges(unittest.TestCase):
    """Test that the changes to sync_tools_playwright.py are correct"""
    
    def test_datetime_utc_usage(self):
        """Test that datetime.now(timezone.utc) works correctly"""
        # This replaces the deprecated datetime.utcnow()
        now = datetime.now(timezone.utc)
        self.assertIsNotNone(now)
        self.assertTrue(hasattr(now, 'year'))
        self.assertTrue(hasattr(now, 'month'))
        self.assertTrue(hasattr(now, 'day'))
        print(f"✅ datetime.now(timezone.utc) works: {now}")
    
    def test_javascript_selectors(self):
        """Verify the JavaScript selectors are targeting correct patterns"""
        # The new selectors should target:
        # 1. .sv-tiles-list a[href*="/tool/"]
        # 2. div[class*="sv-tiles"] a[href*="/tool/"]
        # 3. a[href^="/tool/"]
        
        expected_selectors = [
            '.sv-tiles-list a[href*="/tool/"]',
            'div[class*="sv-tiles"] a[href*="/tool/"]',
            'a[href^="/tool/"]'
        ]
        
        # Read the file and check if these selectors are present
        file_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'sync_tools_playwright.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        for selector in expected_selectors:
            self.assertIn(selector, content, f"Selector '{selector}' should be in the file")
            print(f"✅ Found selector: {selector}")
    
    def test_tool_url_filtering(self):
        """Verify that the tool URL filtering logic is present"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'sync_tools_playwright.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for the filtering comment and logic
        self.assertIn("Only accept tool links with /tool/ pattern", content)
        self.assertIn("!href.includes('/tool/')", content)
        print("✅ Tool URL filtering logic is present")
    
    def test_name_extraction_improvement(self):
        """Verify improved name extraction logic"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'sync_tools_playwright.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for improved name extraction
        self.assertIn("Try to get name from heading first, then link text", content)
        self.assertIn("const heading = container?.querySelector('h1, h2, h3, h4, h5", content)
        self.assertIn("link.getAttribute('title')", content)
        print("✅ Improved name extraction logic is present")
    
    def test_debug_logging(self):
        """Verify debug logging is present"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'sync_tools_playwright.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for debug logging
        self.assertIn("Debug: Show first 3 tool names", content)
        self.assertIn("🔍 Sample tools found:", content)
        print("✅ Debug logging is present")
    
    def test_no_utcnow_deprecation(self):
        """Verify that deprecated datetime.utcnow() is not used"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'sync_tools_playwright.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check that utcnow() is not used
        self.assertNotIn("datetime.utcnow()", content)
        # Check that the new datetime.now(timezone.utc) is used
        self.assertIn("datetime.now(timezone.utc)", content)
        print("✅ No deprecated datetime.utcnow() found, using datetime.now(timezone.utc)")


def run_tests():
    """Run all tests"""
    print("="*60)
    print("🧪 Testing sync_tools_playwright.py Changes")
    print("="*60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSyncToolsPlaywrightChanges)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print("="*60)
        return 0
    else:
        print("❌ Some tests failed")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
