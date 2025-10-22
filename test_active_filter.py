#!/usr/bin/env python3
"""
Test suite for active filter and manual tool creation
Tests the new functionality added to fix the active toggle filter
"""

import requests
import sys
import os
from datetime import datetime

# Get backend URL from environment or use default
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000/api")

class ActiveFilterTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.created_tool_id = None
        
    def log_test(self, test_name, success, message):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def setup_admin_auth(self):
        """Setup admin authentication"""
        try:
            # Create initial admin if not exists
            self.session.post(f"{self.base_url}/admin/create-initial")
            
            # Login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/login",
                json=login_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.admin_token = result["access_token"]
                self.log_test("Admin Login Setup", True, "Admin authentication successful")
                return True
            else:
                self.log_test("Admin Login Setup", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login Setup", False, f"Exception: {str(e)}")
            return False
    
    def test_public_endpoint_filters_inactive_tools(self):
        """Test that GET /api/tools only returns active tools"""
        try:
            response = self.session.get(f"{self.base_url}/tools")
            
            if response.status_code == 200:
                tools = response.json()
                
                # Check that all returned tools have is_active = True
                inactive_tools = [tool for tool in tools if not tool.get('is_active', True)]
                
                if len(inactive_tools) == 0:
                    self.log_test(
                        "Public /api/tools filters inactive",
                        True,
                        f"All {len(tools)} tools returned are active (is_active=True)"
                    )
                else:
                    self.log_test(
                        "Public /api/tools filters inactive",
                        False,
                        f"Found {len(inactive_tools)} inactive tools in public endpoint"
                    )
            else:
                self.log_test("Public /api/tools filters inactive", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Public /api/tools filters inactive", False, f"Exception: {str(e)}")
    
    def test_featured_endpoint_filters_inactive_tools(self):
        """Test that GET /api/tools/featured only returns active featured tools"""
        try:
            response = self.session.get(f"{self.base_url}/tools/featured")
            
            if response.status_code == 200:
                tools = response.json()
                
                # Check that all returned tools are both featured and active
                invalid_tools = [
                    tool for tool in tools 
                    if not tool.get('is_featured', False) or not tool.get('is_active', True)
                ]
                
                if len(invalid_tools) == 0:
                    self.log_test(
                        "Featured /api/tools/featured filters inactive",
                        True,
                        f"All {len(tools)} featured tools are active"
                    )
                else:
                    self.log_test(
                        "Featured /api/tools/featured filters inactive",
                        False,
                        f"Found {len(invalid_tools)} tools that are not featured or not active"
                    )
            else:
                self.log_test("Featured /api/tools/featured filters inactive", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Featured /api/tools/featured filters inactive", False, f"Exception: {str(e)}")
    
    def test_admin_endpoint_shows_all_tools(self):
        """Test that GET /api/admin/tools returns all tools including inactive"""
        if not self.admin_token:
            self.log_test("Admin /api/admin/tools shows all", False, "No admin token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get admin tools
            admin_response = self.session.get(f"{self.base_url}/admin/tools", headers=headers)
            
            # Get public tools
            public_response = self.session.get(f"{self.base_url}/tools")
            
            if admin_response.status_code == 200 and public_response.status_code == 200:
                admin_tools = admin_response.json()
                public_tools = public_response.json()
                
                # Admin should return same or more tools than public
                if len(admin_tools) >= len(public_tools):
                    inactive_count = len(admin_tools) - len(public_tools)
                    self.log_test(
                        "Admin /api/admin/tools shows all",
                        True,
                        f"Admin endpoint returns {len(admin_tools)} tools ({inactive_count} inactive), public returns {len(public_tools)}"
                    )
                else:
                    self.log_test(
                        "Admin /api/admin/tools shows all",
                        False,
                        f"Admin returns fewer tools ({len(admin_tools)}) than public ({len(public_tools)})"
                    )
            else:
                self.log_test(
                    "Admin /api/admin/tools shows all",
                    False,
                    f"HTTP {admin_response.status_code} (admin) / {public_response.status_code} (public)"
                )
                
        except Exception as e:
            self.log_test("Admin /api/admin/tools shows all", False, f"Exception: {str(e)}")
    
    def test_create_new_tool(self):
        """Test POST /api/admin/tools creates a new tool"""
        if not self.admin_token:
            self.log_test("POST /api/admin/tools (create)", False, "No admin token available")
            return
        
        try:
            new_tool = {
                "name": f"Test Tool {datetime.now().strftime('%Y%m%d%H%M%S')}",
                "description": "A test tool created by automated test",
                "category": "Testing",
                "tags": ["test", "automation"],
                "price_type": "Free",
                "website_url": "https://test-tool.example.com",
                "image_url": "https://via.placeholder.com/150"
            }
            
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/tools",
                json=new_tool,
                headers=headers
            )
            
            if response.status_code == 200:
                created_tool = response.json()
                
                # Verify the tool was created with correct defaults
                if (created_tool.get('name') == new_tool['name'] and
                    created_tool.get('is_active') == True and
                    created_tool.get('is_featured') == False and
                    'id' in created_tool):
                    
                    self.created_tool_id = created_tool.get('id')
                    self.log_test(
                        "POST /api/admin/tools (create)",
                        True,
                        f"Tool created successfully with defaults: is_active=True, is_featured=False"
                    )
                else:
                    self.log_test(
                        "POST /api/admin/tools (create)",
                        False,
                        "Tool created but missing expected fields or defaults"
                    )
            else:
                self.log_test("POST /api/admin/tools (create)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/admin/tools (create)", False, f"Exception: {str(e)}")
    
    def test_created_tool_appears_in_public_list(self):
        """Verify newly created tool appears in public list (since it's active by default)"""
        if not self.created_tool_id:
            self.log_test("Verify created tool in public list", False, "No created tool ID available")
            return
        
        try:
            response = self.session.get(f"{self.base_url}/tools")
            
            if response.status_code == 200:
                tools = response.json()
                created_tool_found = any(tool.get('id') == self.created_tool_id for tool in tools)
                
                if created_tool_found:
                    self.log_test(
                        "Verify created tool in public list",
                        True,
                        "Newly created tool appears in public endpoint (is_active=True)"
                    )
                else:
                    self.log_test(
                        "Verify created tool in public list",
                        False,
                        "Newly created tool not found in public endpoint"
                    )
            else:
                self.log_test("Verify created tool in public list", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Verify created tool in public list", False, f"Exception: {str(e)}")
    
    def test_toggle_tool_inactive(self):
        """Test toggling tool to inactive removes it from public list"""
        if not self.admin_token or not self.created_tool_id:
            self.log_test("Toggle tool inactive", False, "No admin token or tool ID available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Toggle tool to inactive
            response = self.session.patch(
                f"{self.base_url}/admin/tools/{self.created_tool_id}/toggle-active",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify it's now inactive
                if result.get('is_active') == False:
                    # Check it's not in public list
                    public_response = self.session.get(f"{self.base_url}/tools")
                    if public_response.status_code == 200:
                        tools = public_response.json()
                        tool_found = any(tool.get('id') == self.created_tool_id for tool in tools)
                        
                        if not tool_found:
                            self.log_test(
                                "Toggle tool inactive",
                                True,
                                "Inactive tool correctly removed from public endpoint"
                            )
                        else:
                            self.log_test(
                                "Toggle tool inactive",
                                False,
                                "Inactive tool still appears in public endpoint"
                            )
                    else:
                        self.log_test("Toggle tool inactive", False, f"Public check failed: HTTP {public_response.status_code}")
                else:
                    self.log_test("Toggle tool inactive", False, "Tool is still active after toggle")
            else:
                self.log_test("Toggle tool inactive", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Toggle tool inactive", False, f"Exception: {str(e)}")
    
    def test_inactive_tool_in_admin_list(self):
        """Verify inactive tool still appears in admin endpoint"""
        if not self.admin_token or not self.created_tool_id:
            self.log_test("Inactive tool in admin list", False, "No admin token or tool ID available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/tools", headers=headers)
            
            if response.status_code == 200:
                tools = response.json()
                tool_found = any(tool.get('id') == self.created_tool_id for tool in tools)
                
                if tool_found:
                    self.log_test(
                        "Inactive tool in admin list",
                        True,
                        "Inactive tool correctly appears in admin endpoint"
                    )
                else:
                    self.log_test(
                        "Inactive tool in admin list",
                        False,
                        "Inactive tool not found in admin endpoint"
                    )
            else:
                self.log_test("Inactive tool in admin list", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Inactive tool in admin list", False, f"Exception: {str(e)}")
    
    def cleanup_test_tool(self):
        """Clean up the test tool"""
        if not self.admin_token or not self.created_tool_id:
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            self.session.delete(
                f"{self.base_url}/admin/tools/{self.created_tool_id}",
                headers=headers
            )
            self.log_test("Cleanup test tool", True, f"Test tool {self.created_tool_id} deleted")
        except Exception as e:
            self.log_test("Cleanup test tool", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🧪 Testing Active Filter and Manual Tool Creation")
        print(f"📡 Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Setup
        if not self.setup_admin_auth():
            print("❌ Failed to setup admin authentication. Skipping admin tests.")
            return False
        
        # Test filtering
        print("\n📋 TESTING ACTIVE FILTER BEHAVIOR")
        print("=" * 80)
        self.test_public_endpoint_filters_inactive_tools()
        self.test_featured_endpoint_filters_inactive_tools()
        self.test_admin_endpoint_shows_all_tools()
        
        # Test manual tool creation
        print("\n🛠️  TESTING MANUAL TOOL CREATION")
        print("=" * 80)
        self.test_create_new_tool()
        self.test_created_tool_appears_in_public_list()
        
        # Test active toggle filter
        print("\n🔄 TESTING ACTIVE TOGGLE FILTER")
        print("=" * 80)
        self.test_toggle_tool_inactive()
        self.test_inactive_tool_in_admin_list()
        
        # Cleanup
        print("\n🧹 CLEANUP")
        print("=" * 80)
        self.cleanup_test_tool()
        
        # Print summary
        print("\n" + "=" * 80)
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = ActiveFilterTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
