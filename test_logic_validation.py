#!/usr/bin/env python3
"""
Logic validation tests for active filter and tool creation
Tests the code logic without requiring a running database
"""

import sys
import re

def test_public_tools_endpoint_has_active_filter():
    """Verify GET /api/tools has is_active filter"""
    with open('server.py', 'r') as f:
        content = f.read()
    
    # Look for the get_tools function and is_active filter nearby
    if 'def get_tools(' in content and 'query = {"is_active": True}' in content:
        print("✅ PASS: GET /api/tools has is_active: True filter")
        return True
    else:
        print("❌ FAIL: GET /api/tools missing is_active: True filter")
        return False

def test_featured_tools_endpoint_has_active_filter():
    """Verify GET /api/tools/featured has is_active filter"""
    with open('server.py', 'r') as f:
        content = f.read()
    
    # Look for the get_featured_tools function with both filters
    if 'def get_featured_tools(' in content and '"is_featured": True, "is_active": True' in content:
        print("✅ PASS: GET /api/tools/featured has both is_featured and is_active filters")
        return True
    else:
        print("❌ FAIL: GET /api/tools/featured missing filters")
        return False

def test_admin_tools_endpoint_exists():
    """Verify GET /api/admin/tools endpoint exists"""
    with open('server.py', 'r') as f:
        content = f.read()
    
    # Check for admin tools endpoint
    if '@api_router.get("/admin/tools"' in content and 'get_all_tools_admin' in content:
        print("✅ PASS: GET /api/admin/tools endpoint exists")
        return True
    else:
        print("❌ FAIL: GET /api/admin/tools endpoint not found")
        return False

def test_create_tool_endpoint_exists():
    """Verify POST /api/admin/tools endpoint exists"""
    with open('server.py', 'r') as f:
        content = f.read()
    
    # Check for create tool endpoint
    if '@api_router.post("/admin/tools"' in content and 'create_tool_admin' in content:
        print("✅ PASS: POST /api/admin/tools endpoint exists")
        return True
    else:
        print("❌ FAIL: POST /api/admin/tools endpoint not found")
        return False

def test_create_tool_sets_defaults():
    """Verify POST /api/admin/tools sets correct defaults"""
    with open('server.py', 'r') as f:
        content = f.read()
    
    # Find the create_tool_admin function
    create_pattern = r'def create_tool_admin\(.*?\):.*?tool_dict = tool_input\.dict\(\)(.*?)tool = Tool\('
    match = re.search(create_pattern, content, re.DOTALL)
    
    if match:
        defaults_code = match.group(1)
        has_active_true = '"is_active"] = True' in defaults_code or "'is_active'] = True" in defaults_code
        has_featured_false = '"is_featured"] = False' in defaults_code or "'is_featured'] = False" in defaults_code
        
        if has_active_true and has_featured_false:
            print("✅ PASS: POST /api/admin/tools sets correct defaults (is_active=True, is_featured=False)")
            return True
        else:
            print(f"❌ FAIL: POST /api/admin/tools missing defaults (has_active_true={has_active_true}, has_featured_false={has_featured_false})")
            return False
    else:
        print("❌ FAIL: Could not find create_tool_admin function logic")
        return False

def test_admin_update_endpoint_exists():
    """Verify PUT /api/admin/tools/{tool_id} endpoint exists"""
    with open('server.py', 'r') as f:
        content = f.read()
    
    # Check for update tool endpoint
    if '@api_router.put("/admin/tools/{tool_id}"' in content and 'update_tool_admin' in content:
        print("✅ PASS: PUT /api/admin/tools/{tool_id} endpoint exists")
        return True
    else:
        print("❌ FAIL: PUT /api/admin/tools/{tool_id} endpoint not found")
        return False

def test_admin_delete_endpoint_exists():
    """Verify DELETE /api/admin/tools/{tool_id} endpoint exists"""
    with open('server.py', 'r') as f:
        content = f.read()
    
    # Check for delete tool endpoint
    if '@api_router.delete("/admin/tools/{tool_id}"' in content and 'delete_tool_admin' in content:
        print("✅ PASS: DELETE /api/admin/tools/{tool_id} endpoint exists")
        return True
    else:
        print("❌ FAIL: DELETE /api/admin/tools/{tool_id} endpoint not found")
        return False

def test_frontend_has_add_button():
    """Verify frontend has Add New Tool button"""
    with open('frontend/src/pages/admin/ToolsManagement.js', 'r') as f:
        content = f.read()
    
    if 'Add New Tool' in content and 'handleAddNew' in content:
        print("✅ PASS: Frontend has 'Add New Tool' button with handler")
        return True
    else:
        print("❌ FAIL: Frontend missing 'Add New Tool' button or handler")
        return False

def test_frontend_fetches_admin_endpoint():
    """Verify frontend fetches from /api/admin/tools"""
    with open('frontend/src/pages/admin/ToolsManagement.js', 'r') as f:
        content = f.read()
    
    if '/admin/tools' in content and 'fetchTools' in content:
        print("✅ PASS: Frontend fetches tools from admin endpoint")
        return True
    else:
        print("❌ FAIL: Frontend not using admin endpoint for fetching tools")
        return False

def test_frontend_handles_create_and_update():
    """Verify frontend handles both create and update operations"""
    with open('frontend/src/pages/admin/ToolsManagement.js', 'r') as f:
        content = f.read()
    
    has_post = 'axios.post' in content and '/admin/tools' in content
    has_put = 'axios.put' in content and '/admin/tools/' in content
    has_conditional = 'editingTool' in content and '?' in content
    
    if has_post and has_put and has_conditional:
        print("✅ PASS: Frontend handles both create (POST) and update (PUT) operations")
        return True
    else:
        print(f"❌ FAIL: Frontend missing create/update logic (has_post={has_post}, has_put={has_put}, has_conditional={has_conditional})")
        return False

def test_frontend_modal_title_dynamic():
    """Verify frontend modal title is dynamic"""
    with open('frontend/src/pages/admin/ToolsManagement.js', 'r') as f:
        content = f.read()
    
    # Check for dynamic modal title
    if "editingTool ? 'Edit Tool' : 'Add New Tool'" in content:
        print("✅ PASS: Frontend modal title is dynamic based on add/edit mode")
        return True
    else:
        print("❌ FAIL: Frontend modal title is not dynamic")
        return False

def main():
    """Run all logic validation tests"""
    print("🧪 Running Logic Validation Tests")
    print("=" * 80)
    
    tests = [
        test_public_tools_endpoint_has_active_filter,
        test_featured_tools_endpoint_has_active_filter,
        test_admin_tools_endpoint_exists,
        test_create_tool_endpoint_exists,
        test_create_tool_sets_defaults,
        test_admin_update_endpoint_exists,
        test_admin_delete_endpoint_exists,
        test_frontend_has_add_button,
        test_frontend_fetches_admin_endpoint,
        test_frontend_handles_create_and_update,
        test_frontend_modal_title_dynamic,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    print(f"Success Rate: {(sum(results)/len(results))*100:.1f}%")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
