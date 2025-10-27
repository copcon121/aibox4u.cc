#!/usr/bin/env python3
"""
AI Tools Directory Backend API Test Suite
Tests all backend API endpoints with comprehensive scenarios
"""

import requests
import json
import sys
import os
from datetime import datetime
import uuid

# Get backend URL from environment
BACKEND_URL = "https://admin-tools-panel.preview.emergentagent.com/api"

class APITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_tool_id = None
        self.admin_token = None
        self.created_page_id = None

    @staticmethod
    def _normalize_tools_payload(payload):
        """Return a list of tools regardless of response envelope format."""
        if isinstance(payload, dict):
            items = payload.get('items')
            if isinstance(items, list):
                return items
            return []
        if isinstance(payload, list):
            return payload
        return []

    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def test_get_all_tools(self):
        """Test GET /api/tools - Get all tools"""
        try:
            response = self.session.get(f"{self.base_url}/tools")
            
            if response.status_code == 200:
                tools_payload = response.json()
                tools = self._normalize_tools_payload(tools_payload)
                if len(tools) > 0:
                    total = tools_payload.get('total') if isinstance(tools_payload, dict) else len(tools)
                    self.log_test("GET /api/tools", True, f"Retrieved {len(tools)} tools successfully (total: {total})")
                    return tools
                else:
                    self.log_test("GET /api/tools", False, "No tools returned or invalid format")
                    return []
            else:
                self.log_test("GET /api/tools", False, f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("GET /api/tools", False, f"Exception: {str(e)}")
            return []
    
    def test_get_tools_with_search(self):
        """Test GET /api/tools with search parameter"""
        try:
            response = self.session.get(f"{self.base_url}/tools?search=ChatGPT")
            
            if response.status_code == 200:
                tools_payload = response.json()
                tools = self._normalize_tools_payload(tools_payload)
                # Check if ChatGPT is in results
                chatgpt_found = any(tool.get('name', '').lower() == 'chatgpt' for tool in tools)
                if chatgpt_found:
                    self.log_test("GET /api/tools?search=ChatGPT", True, f"Search returned {len(tools)} tools, ChatGPT found")
                else:
                    self.log_test("GET /api/tools?search=ChatGPT", False, f"Search returned {len(tools)} tools, but ChatGPT not found")
            else:
                self.log_test("GET /api/tools?search=ChatGPT", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/tools?search=ChatGPT", False, f"Exception: {str(e)}")
    
    def test_get_tools_with_category_filter(self):
        """Test GET /api/tools with category filter"""
        try:
            response = self.session.get(f"{self.base_url}/tools?category=Chatbot")
            
            if response.status_code == 200:
                tools = self._normalize_tools_payload(response.json())
                # Check if all returned tools are in Chatbot category
                all_chatbot = all(tool.get('category') == 'Chatbot' for tool in tools)
                if all_chatbot and len(tools) > 0:
                    self.log_test("GET /api/tools?category=Chatbot", True, f"Category filter returned {len(tools)} chatbot tools")
                elif len(tools) == 0:
                    self.log_test("GET /api/tools?category=Chatbot", True, "Category filter returned 0 tools (valid if no chatbots exist)")
                else:
                    self.log_test("GET /api/tools?category=Chatbot", False, "Category filter returned tools from other categories")
            else:
                self.log_test("GET /api/tools?category=Chatbot", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/tools?category=Chatbot", False, f"Exception: {str(e)}")
    
    def test_get_tools_with_price_filter(self):
        """Test GET /api/tools with price filter"""
        try:
            response = self.session.get(f"{self.base_url}/tools?price_type=Freemium")
            
            if response.status_code == 200:
                tools = self._normalize_tools_payload(response.json())
                # Check if all returned tools are Freemium
                all_freemium = all(tool.get('price_type') == 'Freemium' for tool in tools)
                if all_freemium and len(tools) > 0:
                    self.log_test("GET /api/tools?price_type=Freemium", True, f"Price filter returned {len(tools)} freemium tools")
                elif len(tools) == 0:
                    self.log_test("GET /api/tools?price_type=Freemium", True, "Price filter returned 0 tools (valid if no freemium tools exist)")
                else:
                    self.log_test("GET /api/tools?price_type=Freemium", False, "Price filter returned tools with other price types")
            else:
                self.log_test("GET /api/tools?price_type=Freemium", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/tools?price_type=Freemium", False, f"Exception: {str(e)}")
    
    def test_get_tools_with_multiple_filters(self):
        """Test GET /api/tools with multiple filters combined"""
        try:
            response = self.session.get(f"{self.base_url}/tools?category=Search&price_type=Freemium")
            
            if response.status_code == 200:
                tools = self._normalize_tools_payload(response.json())
                # Check if all returned tools match both filters
                valid_tools = all(
                    tool.get('category') == 'Search' and tool.get('price_type') == 'Freemium'
                    for tool in tools
                )
                if valid_tools:
                    self.log_test("GET /api/tools (multiple filters)", True, f"Multiple filters returned {len(tools)} matching tools")
                else:
                    self.log_test("GET /api/tools (multiple filters)", False, "Multiple filters returned tools that don't match criteria")
            else:
                self.log_test("GET /api/tools (multiple filters)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/tools (multiple filters)", False, f"Exception: {str(e)}")
    
    def test_get_featured_tools(self):
        """Test GET /api/tools/featured - Should return Perplexity and Comet Browser"""
        try:
            response = self.session.get(f"{self.base_url}/tools/featured")
            
            if response.status_code == 200:
                tools = response.json()
                if isinstance(tools, list):
                    # Check if Perplexity and Comet Browser are in featured tools
                    tool_names = [tool.get('name', '') for tool in tools]
                    has_perplexity = 'Perplexity' in tool_names
                    has_comet = 'Comet Browser' in tool_names
                    
                    # Check if all tools have is_featured=True
                    all_featured = all(tool.get('is_featured', False) for tool in tools)
                    
                    if has_perplexity and has_comet and all_featured:
                        self.log_test("GET /api/tools/featured", True, f"Featured tools returned correctly: {len(tools)} tools including Perplexity and Comet Browser")
                    elif not all_featured:
                        self.log_test("GET /api/tools/featured", False, "Some returned tools have is_featured=False")
                    else:
                        self.log_test("GET /api/tools/featured", False, f"Missing expected featured tools. Found: {tool_names}")
                else:
                    self.log_test("GET /api/tools/featured", False, "Invalid response format")
            else:
                self.log_test("GET /api/tools/featured", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/tools/featured", False, f"Exception: {str(e)}")
    
    def test_get_single_tool_valid(self, tools):
        """Test GET /api/tools/{id} with valid tool ID"""
        if not tools:
            self.log_test("GET /api/tools/{id} (valid)", False, "No tools available to test with")
            return
            
        try:
            # Use the first tool's ID
            tool_id = tools[0].get('id')
            if not tool_id:
                self.log_test("GET /api/tools/{id} (valid)", False, "No valid tool ID found")
                return
                
            response = self.session.get(f"{self.base_url}/tools/{tool_id}")
            
            if response.status_code == 200:
                tool = response.json()
                if isinstance(tool, dict) and tool.get('id') == tool_id:
                    self.log_test("GET /api/tools/{id} (valid)", True, f"Retrieved tool '{tool.get('name')}' successfully")
                else:
                    self.log_test("GET /api/tools/{id} (valid)", False, "Invalid tool data returned")
            else:
                self.log_test("GET /api/tools/{id} (valid)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/tools/{id} (valid)", False, f"Exception: {str(e)}")
    
    def test_get_single_tool_invalid(self):
        """Test GET /api/tools/{id} with invalid tool ID (should return 404)"""
        try:
            invalid_id = "invalid-tool-id-12345"
            response = self.session.get(f"{self.base_url}/tools/{invalid_id}")
            
            if response.status_code == 404:
                self.log_test("GET /api/tools/{id} (invalid)", True, "Correctly returned 404 for invalid tool ID")
            else:
                self.log_test("GET /api/tools/{id} (invalid)", False, f"Expected 404, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/tools/{id} (invalid)", False, f"Exception: {str(e)}")
    
    def test_get_categories(self):
        """Test GET /api/categories - Should return list of unique categories"""
        try:
            response = self.session.get(f"{self.base_url}/categories")
            
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list) and len(categories) > 0:
                    # Check if categories are unique
                    unique_categories = len(categories) == len(set(categories))
                    if unique_categories:
                        self.log_test("GET /api/categories", True, f"Retrieved {len(categories)} unique categories: {categories}")
                    else:
                        self.log_test("GET /api/categories", False, "Categories list contains duplicates")
                else:
                    self.log_test("GET /api/categories", False, "No categories returned or invalid format")
            else:
                self.log_test("GET /api/categories", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/categories", False, f"Exception: {str(e)}")
    
    def test_get_price_types(self):
        """Test GET /api/price-types - Should return ["All", "Free", "Paid", "Freemium"]"""
        try:
            response = self.session.get(f"{self.base_url}/price-types")
            
            if response.status_code == 200:
                price_types = response.json()
                expected_types = ["All", "Free", "Paid", "Freemium"]
                
                if isinstance(price_types, list) and set(price_types) == set(expected_types):
                    self.log_test("GET /api/price-types", True, f"Correctly returned price types: {price_types}")
                else:
                    self.log_test("GET /api/price-types", False, f"Expected {expected_types}, got {price_types}")
            else:
                self.log_test("GET /api/price-types", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/price-types", False, f"Exception: {str(e)}")
    
    def test_create_tool(self):
        """Test POST /api/tools - Create new tool"""
        try:
            new_tool = {
                "name": "TestAI Assistant",
                "description": "A comprehensive AI assistant for productivity and creativity tasks",
                "category": "Productivity",
                "tags": ["AI", "Assistant", "Productivity", "Automation"],
                "price_type": "Freemium",
                "website_url": "https://testai-assistant.com",
                "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=500&h=300&fit=crop",
                "is_featured": False
            }
            
            response = self.session.post(
                f"{self.base_url}/tools",
                json=new_tool,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                created_tool = response.json()
                if isinstance(created_tool, dict) and created_tool.get('name') == new_tool['name']:
                    self.created_tool_id = created_tool.get('id')
                    self.log_test("POST /api/tools", True, f"Successfully created tool '{created_tool.get('name')}' with ID: {self.created_tool_id}")
                    return created_tool
                else:
                    self.log_test("POST /api/tools", False, "Invalid tool data returned after creation")
            else:
                self.log_test("POST /api/tools", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/tools", False, f"Exception: {str(e)}")
        
        return None
    
    def test_verify_created_tool(self):
        """Verify created tool appears in GET /api/tools"""
        if not self.created_tool_id:
            self.log_test("Verify created tool in list", False, "No created tool ID available")
            return
            
        try:
            response = self.session.get(f"{self.base_url}/tools")
            
            if response.status_code == 200:
                tools = response.json()
                created_tool_found = any(tool.get('id') == self.created_tool_id for tool in tools)
                
                if created_tool_found:
                    self.log_test("Verify created tool in list", True, "Created tool appears in tools list")
                else:
                    self.log_test("Verify created tool in list", False, "Created tool not found in tools list")
            else:
                self.log_test("Verify created tool in list", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Verify created tool in list", False, f"Exception: {str(e)}")
    
    def test_update_tool(self):
        """Test PUT /api/tools/{id} - Update existing tool"""
        if not self.created_tool_id:
            self.log_test("PUT /api/tools/{id} (valid)", False, "No created tool ID available for update")
            return
            
        try:
            updated_data = {
                "name": "TestAI Assistant Pro",
                "description": "An advanced AI assistant with premium features for enterprise productivity",
                "category": "Enterprise",
                "tags": ["AI", "Assistant", "Enterprise", "Premium"],
                "price_type": "Paid",
                "website_url": "https://testai-assistant-pro.com",
                "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=500&h=300&fit=crop",
                "is_featured": True
            }
            
            response = self.session.put(
                f"{self.base_url}/tools/{self.created_tool_id}",
                json=updated_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                updated_tool = response.json()
                if (isinstance(updated_tool, dict) and 
                    updated_tool.get('name') == updated_data['name'] and
                    updated_tool.get('category') == updated_data['category']):
                    self.log_test("PUT /api/tools/{id} (valid)", True, f"Successfully updated tool to '{updated_tool.get('name')}'")
                else:
                    self.log_test("PUT /api/tools/{id} (valid)", False, "Tool update did not reflect expected changes")
            else:
                self.log_test("PUT /api/tools/{id} (valid)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("PUT /api/tools/{id} (valid)", False, f"Exception: {str(e)}")
    
    def test_update_nonexistent_tool(self):
        """Test PUT /api/tools/{id} with non-existent tool (should return 404)"""
        try:
            invalid_id = "nonexistent-tool-id-12345"
            updated_data = {
                "name": "Should Not Work",
                "description": "This update should fail",
                "category": "Test",
                "tags": ["Test"],
                "price_type": "Free",
                "website_url": "https://example.com"
            }
            
            response = self.session.put(
                f"{self.base_url}/tools/{invalid_id}",
                json=updated_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 404:
                self.log_test("PUT /api/tools/{id} (invalid)", True, "Correctly returned 404 for non-existent tool update")
            else:
                self.log_test("PUT /api/tools/{id} (invalid)", False, f"Expected 404, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("PUT /api/tools/{id} (invalid)", False, f"Exception: {str(e)}")
    
    def test_delete_tool(self):
        """Test DELETE /api/tools/{id} - Delete existing tool"""
        if not self.created_tool_id:
            self.log_test("DELETE /api/tools/{id} (valid)", False, "No created tool ID available for deletion")
            return
            
        try:
            response = self.session.delete(f"{self.base_url}/tools/{self.created_tool_id}")
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict) and "deleted" in result.get("message", "").lower():
                    self.log_test("DELETE /api/tools/{id} (valid)", True, f"Successfully deleted tool with ID: {self.created_tool_id}")
                    
                    # Verify tool is actually deleted
                    verify_response = self.session.get(f"{self.base_url}/tools/{self.created_tool_id}")
                    if verify_response.status_code == 404:
                        self.log_test("Verify tool deletion", True, "Deleted tool no longer accessible")
                    else:
                        self.log_test("Verify tool deletion", False, "Deleted tool still accessible")
                else:
                    self.log_test("DELETE /api/tools/{id} (valid)", False, "Unexpected response format for deletion")
            else:
                self.log_test("DELETE /api/tools/{id} (valid)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("DELETE /api/tools/{id} (valid)", False, f"Exception: {str(e)}")
    
    def test_delete_nonexistent_tool(self):
        """Test DELETE /api/tools/{id} with non-existent tool (should return 404)"""
        try:
            invalid_id = "nonexistent-tool-id-12345"
            response = self.session.delete(f"{self.base_url}/tools/{invalid_id}")
            
            if response.status_code == 404:
                self.log_test("DELETE /api/tools/{id} (invalid)", True, "Correctly returned 404 for non-existent tool deletion")
            else:
                self.log_test("DELETE /api/tools/{id} (invalid)", False, f"Expected 404, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("DELETE /api/tools/{id} (invalid)", False, f"Exception: {str(e)}")

    # ============================================
    # ADMIN ENDPOINT TESTS
    # ============================================
    
    def test_create_initial_admin(self):
        """Create initial admin if not exists"""
        try:
            response = self.session.post(f"{self.base_url}/admin/create-initial")
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Create Initial Admin", True, f"Initial admin created: {result.get('username')}")
            elif response.status_code == 400:
                # Admin already exists - this is fine
                self.log_test("Create Initial Admin", True, "Admin already exists (expected)")
            else:
                self.log_test("Create Initial Admin", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Create Initial Admin", False, f"Exception: {str(e)}")
    
    def test_admin_login_success(self):
        """Test POST /api/admin/login with correct credentials"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "access_token" in result and "token_type" in result:
                    self.admin_token = result["access_token"]
                    self.log_test("POST /api/admin/login (success)", True, f"Login successful, token received: {result['token_type']}")
                else:
                    self.log_test("POST /api/admin/login (success)", False, "Missing access_token or token_type in response")
            else:
                self.log_test("POST /api/admin/login (success)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/admin/login (success)", False, f"Exception: {str(e)}")
    
    def test_admin_login_failure(self):
        """Test POST /api/admin/login with incorrect credentials"""
        try:
            login_data = {
                "username": "admin",
                "password": "wrongpassword"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                self.log_test("POST /api/admin/login (failure)", True, "Correctly returned 401 for wrong credentials")
            else:
                self.log_test("POST /api/admin/login (failure)", False, f"Expected 401, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/admin/login (failure)", False, f"Exception: {str(e)}")
    
    def test_admin_verify_with_token(self):
        """Test GET /api/admin/verify with valid token"""
        if not self.admin_token:
            self.log_test("GET /api/admin/verify (with token)", False, "No admin token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/verify", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("username") == "admin" and result.get("authenticated") is True:
                    self.log_test("GET /api/admin/verify (with token)", True, f"Token verified for user: {result['username']}")
                else:
                    self.log_test("GET /api/admin/verify (with token)", False, "Invalid verification response")
            else:
                self.log_test("GET /api/admin/verify (with token)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/admin/verify (with token)", False, f"Exception: {str(e)}")
    
    def test_admin_verify_without_token(self):
        """Test GET /api/admin/verify without token (should return 401)"""
        try:
            response = self.session.get(f"{self.base_url}/admin/verify")
            
            if response.status_code == 401:
                self.log_test("GET /api/admin/verify (no token)", True, "Correctly returned 401 for missing token")
            else:
                self.log_test("GET /api/admin/verify (no token)", False, f"Expected 401, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/admin/verify (no token)", False, f"Exception: {str(e)}")
    
    def test_toggle_tool_active(self, tools):
        """Test PATCH /api/admin/tools/{id}/toggle-active"""
        if not self.admin_token:
            self.log_test("PATCH /api/admin/tools/{id}/toggle-active", False, "No admin token available")
            return
            
        if not tools:
            self.log_test("PATCH /api/admin/tools/{id}/toggle-active", False, "No tools available to test with")
            return
            
        try:
            tool_id = tools[0].get('id')
            original_status = tools[0].get('is_active', True)
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.patch(f"{self.base_url}/admin/tools/{tool_id}/toggle-active", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                new_status = result.get("is_active")
                if new_status != original_status:
                    self.log_test("PATCH /api/admin/tools/{id}/toggle-active", True, f"Tool active status toggled from {original_status} to {new_status}")
                else:
                    self.log_test("PATCH /api/admin/tools/{id}/toggle-active", False, "Tool active status did not change")
            else:
                self.log_test("PATCH /api/admin/tools/{id}/toggle-active", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("PATCH /api/admin/tools/{id}/toggle-active", False, f"Exception: {str(e)}")
    
    def test_toggle_tool_featured(self, tools):
        """Test PATCH /api/admin/tools/{id}/toggle-featured"""
        if not self.admin_token:
            self.log_test("PATCH /api/admin/tools/{id}/toggle-featured", False, "No admin token available")
            return
            
        if not tools:
            self.log_test("PATCH /api/admin/tools/{id}/toggle-featured", False, "No tools available to test with")
            return
            
        try:
            tool_id = tools[0].get('id')
            original_status = tools[0].get('is_featured', False)
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.patch(f"{self.base_url}/admin/tools/{tool_id}/toggle-featured", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                new_status = result.get("is_featured")
                if new_status != original_status:
                    self.log_test("PATCH /api/admin/tools/{id}/toggle-featured", True, f"Tool featured status toggled from {original_status} to {new_status}")
                else:
                    self.log_test("PATCH /api/admin/tools/{id}/toggle-featured", False, "Tool featured status did not change")
            else:
                self.log_test("PATCH /api/admin/tools/{id}/toggle-featured", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("PATCH /api/admin/tools/{id}/toggle-featured", False, f"Exception: {str(e)}")
    
    def test_get_admin_statistics(self):
        """Test GET /api/admin/stats"""
        if not self.admin_token:
            self.log_test("GET /api/admin/stats", False, "No admin token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_tools", "active_tools", "featured_tools", "total_categories", "tools_by_category", "tools_by_price_type"]
                
                if all(field in stats for field in required_fields):
                    self.log_test("GET /api/admin/stats", True, f"Statistics retrieved: {stats['total_tools']} total tools, {stats['active_tools']} active, {stats['featured_tools']} featured")
                else:
                    missing_fields = [field for field in required_fields if field not in stats]
                    self.log_test("GET /api/admin/stats", False, f"Missing required fields: {missing_fields}")
            else:
                self.log_test("GET /api/admin/stats", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/admin/stats", False, f"Exception: {str(e)}")
    
    def test_get_site_settings(self):
        """Test GET /api/admin/site-settings"""
        if not self.admin_token:
            self.log_test("GET /api/admin/site-settings", False, "No admin token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/site-settings", headers=headers)
            
            if response.status_code == 200:
                settings = response.json()
                if "site_name" in settings and "site_description" in settings:
                    self.log_test("GET /api/admin/site-settings", True, f"Site settings retrieved: {settings.get('site_name')}")
                else:
                    self.log_test("GET /api/admin/site-settings", False, "Invalid site settings format")
            else:
                self.log_test("GET /api/admin/site-settings", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/admin/site-settings", False, f"Exception: {str(e)}")
    
    def test_update_site_settings(self):
        """Test PUT /api/admin/site-settings"""
        if not self.admin_token:
            self.log_test("PUT /api/admin/site-settings", False, "No admin token available")
            return
            
        try:
            settings_data = {
                "site_name": "AI Tools Directory Test",
                "site_description": "Test Description for AI Tools Directory",
                "site_logo_url": "https://example.com/test-logo.png"
            }
            
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.put(
                f"{self.base_url}/admin/site-settings",
                json=settings_data,
                headers=headers
            )
            
            if response.status_code == 200:
                updated_settings = response.json()
                if updated_settings.get("site_name") == settings_data["site_name"]:
                    self.log_test("PUT /api/admin/site-settings", True, f"Site settings updated successfully: {updated_settings.get('site_name')}")
                else:
                    self.log_test("PUT /api/admin/site-settings", False, "Site settings update did not reflect changes")
            else:
                self.log_test("PUT /api/admin/site-settings", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("PUT /api/admin/site-settings", False, f"Exception: {str(e)}")
    
    def test_get_all_pages(self):
        """Test GET /api/admin/pages"""
        if not self.admin_token:
            self.log_test("GET /api/admin/pages", False, "No admin token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/pages", headers=headers)
            
            if response.status_code == 200:
                pages = response.json()
                if isinstance(pages, list):
                    self.log_test("GET /api/admin/pages", True, f"Retrieved {len(pages)} pages")
                else:
                    self.log_test("GET /api/admin/pages", False, "Invalid pages response format")
            else:
                self.log_test("GET /api/admin/pages", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/admin/pages", False, f"Exception: {str(e)}")
    
    def test_create_page(self):
        """Test POST /api/admin/pages"""
        if not self.admin_token:
            self.log_test("POST /api/admin/pages", False, "No admin token available")
            return
            
        try:
            page_data = {
                "title": "About Us Test",
                "slug": "about-us-test",
                "content": "This is a test about us page content with comprehensive information about our AI Tools Directory platform.",
                "is_published": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/pages",
                json=page_data,
                headers=headers
            )
            
            if response.status_code == 200:
                created_page = response.json()
                if created_page.get("title") == page_data["title"] and created_page.get("slug") == page_data["slug"]:
                    self.created_page_id = created_page.get("id")
                    self.log_test("POST /api/admin/pages", True, f"Page created successfully: '{created_page.get('title')}' with ID: {self.created_page_id}")
                else:
                    self.log_test("POST /api/admin/pages", False, "Page creation did not return expected data")
            else:
                self.log_test("POST /api/admin/pages", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/admin/pages", False, f"Exception: {str(e)}")
    
    def test_create_page_duplicate_slug(self):
        """Test POST /api/admin/pages with duplicate slug (should return 400)"""
        if not self.admin_token:
            self.log_test("POST /api/admin/pages (duplicate slug)", False, "No admin token available")
            return
            
        try:
            page_data = {
                "title": "Another About Us",
                "slug": "about-us-test",  # Same slug as previous test
                "content": "This should fail due to duplicate slug.",
                "is_published": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/pages",
                json=page_data,
                headers=headers
            )
            
            if response.status_code == 400:
                self.log_test("POST /api/admin/pages (duplicate slug)", True, "Correctly returned 400 for duplicate slug")
            else:
                self.log_test("POST /api/admin/pages (duplicate slug)", False, f"Expected 400, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/admin/pages (duplicate slug)", False, f"Exception: {str(e)}")
    
    def test_update_page(self):
        """Test PUT /api/admin/pages/{id}"""
        if not self.admin_token:
            self.log_test("PUT /api/admin/pages/{id}", False, "No admin token available")
            return
            
        if not self.created_page_id:
            self.log_test("PUT /api/admin/pages/{id}", False, "No created page ID available")
            return
            
        try:
            updated_data = {
                "title": "About Us Updated",
                "slug": "about-us-updated",
                "content": "This is the updated content for our about us page with more detailed information.",
                "is_published": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.put(
                f"{self.base_url}/admin/pages/{self.created_page_id}",
                json=updated_data,
                headers=headers
            )
            
            if response.status_code == 200:
                updated_page = response.json()
                if updated_page.get("title") == updated_data["title"] and updated_page.get("slug") == updated_data["slug"]:
                    self.log_test("PUT /api/admin/pages/{id}", True, f"Page updated successfully: '{updated_page.get('title')}'")
                else:
                    self.log_test("PUT /api/admin/pages/{id}", False, "Page update did not reflect changes")
            else:
                self.log_test("PUT /api/admin/pages/{id}", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("PUT /api/admin/pages/{id}", False, f"Exception: {str(e)}")
    
    def test_get_public_page(self):
        """Test GET /api/pages/{slug} - Public endpoint (no auth required)"""
        try:
            # Use the updated slug from the previous test
            slug = "about-us-updated"
            response = self.session.get(f"{self.base_url}/pages/{slug}")
            
            if response.status_code == 200:
                page = response.json()
                if page.get("slug") == slug and page.get("is_published") is True:
                    self.log_test("GET /api/pages/{slug} (public)", True, f"Public page retrieved: '{page.get('title')}'")
                else:
                    self.log_test("GET /api/pages/{slug} (public)", False, "Invalid public page data")
            elif response.status_code == 404:
                self.log_test("GET /api/pages/{slug} (public)", False, "Page not found - may not be published or slug incorrect")
            else:
                self.log_test("GET /api/pages/{slug} (public)", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/pages/{slug} (public)", False, f"Exception: {str(e)}")
    
    def test_get_public_page_nonexistent(self):
        """Test GET /api/pages/{slug} with non-existent slug (should return 404)"""
        try:
            slug = "nonexistent-page-slug"
            response = self.session.get(f"{self.base_url}/pages/{slug}")
            
            if response.status_code == 404:
                self.log_test("GET /api/pages/{slug} (nonexistent)", True, "Correctly returned 404 for non-existent page")
            else:
                self.log_test("GET /api/pages/{slug} (nonexistent)", False, f"Expected 404, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/pages/{slug} (nonexistent)", False, f"Exception: {str(e)}")
    
    def test_delete_page(self):
        """Test DELETE /api/admin/pages/{id}"""
        if not self.admin_token:
            self.log_test("DELETE /api/admin/pages/{id}", False, "No admin token available")
            return
            
        if not self.created_page_id:
            self.log_test("DELETE /api/admin/pages/{id}", False, "No created page ID available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.delete(f"{self.base_url}/admin/pages/{self.created_page_id}", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if "deleted" in result.get("message", "").lower():
                    self.log_test("DELETE /api/admin/pages/{id}", True, f"Page deleted successfully: {self.created_page_id}")
                    
                    # Verify page is actually deleted
                    verify_response = self.session.get(f"{self.base_url}/admin/pages/{self.created_page_id}", headers=headers)
                    if verify_response.status_code == 404:
                        self.log_test("Verify page deletion", True, "Deleted page no longer accessible")
                    else:
                        self.log_test("Verify page deletion", False, "Deleted page still accessible")
                else:
                    self.log_test("DELETE /api/admin/pages/{id}", False, "Unexpected response format for deletion")
            else:
                self.log_test("DELETE /api/admin/pages/{id}", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("DELETE /api/admin/pages/{id}", False, f"Exception: {str(e)}")
    
    def test_admin_endpoints_without_auth(self):
        """Test admin endpoints without authentication (should return 401)"""
        admin_endpoints = [
            ("GET", "/admin/verify"),
            ("GET", "/admin/stats"),
            ("GET", "/admin/site-settings"),
            ("GET", "/admin/pages")
        ]
        
        for method, endpoint in admin_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 401:
                    self.log_test(f"{method} {endpoint} (no auth)", True, "Correctly returned 401 for missing authentication")
                else:
                    self.log_test(f"{method} {endpoint} (no auth)", False, f"Expected 401, got HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"{method} {endpoint} (no auth)", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all API tests in sequence"""
        print(f"🚀 Starting AI Tools Directory Backend API Tests")
        print(f"📡 Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test basic retrieval first
        tools = self.test_get_all_tools()
        
        # Test filtering and search
        self.test_get_tools_with_search()
        self.test_get_tools_with_category_filter()
        self.test_get_tools_with_price_filter()
        self.test_get_tools_with_multiple_filters()
        
        # Test featured tools
        self.test_get_featured_tools()
        
        # Test single tool retrieval
        self.test_get_single_tool_valid(tools)
        self.test_get_single_tool_invalid()
        
        # Test metadata endpoints
        self.test_get_categories()
        self.test_get_price_types()
        
        # Test CRUD operations
        self.test_create_tool()
        self.test_verify_created_tool()
        self.test_update_tool()
        self.test_update_nonexistent_tool()
        self.test_delete_tool()
        self.test_delete_nonexistent_tool()
        
        print("\n" + "=" * 80)
        print("🔐 ADMIN AUTHENTICATION & AUTHORIZATION TESTS")
        print("=" * 80)
        
        # Setup admin and test authentication
        self.test_create_initial_admin()
        self.test_admin_login_success()
        self.test_admin_login_failure()
        self.test_admin_verify_with_token()
        self.test_admin_verify_without_token()
        
        # Test admin endpoints without auth (should fail)
        self.test_admin_endpoints_without_auth()
        
        print("\n" + "=" * 80)
        print("⚙️  ADMIN TOOL MANAGEMENT TESTS")
        print("=" * 80)
        
        # Test admin tool management
        self.test_toggle_tool_active(tools)
        self.test_toggle_tool_featured(tools)
        self.test_get_admin_statistics()
        
        print("\n" + "=" * 80)
        print("🌐 SITE SETTINGS TESTS")
        print("=" * 80)
        
        # Test site settings
        self.test_get_site_settings()
        self.test_update_site_settings()
        
        print("\n" + "=" * 80)
        print("📄 PAGES MANAGEMENT TESTS")
        print("=" * 80)
        
        # Test pages CRUD
        self.test_get_all_pages()
        self.test_create_page()
        self.test_create_page_duplicate_slug()
        self.test_update_page()
        self.test_get_public_page()
        self.test_get_public_page_nonexistent()
        self.test_delete_page()
        
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
    tester = APITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()