"""
Comprehensive Feature Testing Script for Gruha Alankara
Tests all major functionality including new features.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"      {details}")

def test_home_page():
    """Test if home page loads successfully."""
    try:
        response = requests.get(f"{BASE_URL}/")
        passed = response.status_code == 200 and "Gruha Alankara" in response.text
        print_test("Home Page", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Home Page", False, f"Error: {str(e)}")
        return False

def test_catalog_page():
    """Test if furniture catalog loads."""
    try:
        response = requests.get(f"{BASE_URL}/orders/catalog")
        passed = response.status_code == 200 and "Furniture Catalog" in response.text
        print_test("Furniture Catalog", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Furniture Catalog", False, f"Error: {str(e)}")
        return False

def test_registration_page():
    """Test if registration page loads."""
    try:
        response = requests.get(f"{BASE_URL}/register")
        passed = response.status_code == 200 and "Register" in response.text
        print_test("Registration Page", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Registration Page", False, f"Error: {str(e)}")
        return False

def test_login_page():
    """Test if login page loads."""
    try:
        response = requests.get(f"{BASE_URL}/login")
        passed = response.status_code == 200 and "Login" in response.text
        print_test("Login Page", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Login Page", False, f"Error: {str(e)}")
        return False

def test_api_models_endpoint():
    """Test if API models endpoint returns furniture data."""
    try:
        # Create a session to handle cookies
        session = requests.Session()
        
        # First, try to access without login (should require auth)
        response = session.get(f"{BASE_URL}/api/models")
        
        # Check if it returns 401 (unauthorized) or 200 with data
        if response.status_code == 401:
            print_test("API Models Endpoint (Auth Required)", True, "Correctly requires authentication")
            return True
        elif response.status_code == 200:
            data = response.json()
            passed = isinstance(data, dict) and len(data) > 0
            print_test("API Models Endpoint", passed, f"Found {len(data)} furniture types")
            return passed
        else:
            print_test("API Models Endpoint", False, f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_test("API Models Endpoint", False, f"Error: {str(e)}")
        return False

def test_database_tables():
    """Test if all database tables exist."""
    try:
        from app import create_app
        from models import db, User, Design, FurniturePlacement, FurnitureItem, Order, OrderItem
        
        app = create_app()
        with app.app_context():
            # Check if tables exist by querying them
            user_count = User.query.count()
            design_count = Design.query.count()
            furniture_count = FurnitureItem.query.count()
            order_count = Order.query.count()
            
            passed = furniture_count > 0  # Should have seeded furniture
            print_test("Database Tables", passed, 
                      f"Users: {user_count}, Designs: {design_count}, Furniture: {furniture_count}, Orders: {order_count}")
            return passed
    except Exception as e:
        print_test("Database Tables", False, f"Error: {str(e)}")
        return False

def test_ai_cache_directory():
    """Test if AI cache directory was created."""
    try:
        import os
        cache_dir = os.path.join(os.path.dirname(__file__), 'ai_cache')
        exists = os.path.exists(cache_dir)
        print_test("AI Cache Directory", exists, f"Path: {cache_dir}")
        return exists
    except Exception as e:
        print_test("AI Cache Directory", False, f"Error: {str(e)}")
        return False

def test_static_files():
    """Test if static files are accessible."""
    try:
        css_response = requests.get(f"{BASE_URL}/static/css/style.css")
        js_response = requests.get(f"{BASE_URL}/static/js/main.js")
        studio_js_response = requests.get(f"{BASE_URL}/static/js/studio.js")
        
        passed = (css_response.status_code == 200 and 
                 js_response.status_code == 200 and 
                 studio_js_response.status_code == 200)
        
        print_test("Static Files", passed, 
                  f"CSS: {css_response.status_code}, JS: {js_response.status_code}, Studio: {studio_js_response.status_code}")
        return passed
    except Exception as e:
        print_test("Static Files", False, f"Error: {str(e)}")
        return False

def test_gltf_loader_import():
    """Test if GLTFLoader is properly imported in studio.js."""
    try:
        response = requests.get(f"{BASE_URL}/static/js/studio.js")
        content = response.text
        has_gltf_import = "GLTFLoader" in content
        has_gltf_loader_var = "gltfLoader" in content
        has_load_function = "loadGLTFModel" in content
        
        passed = has_gltf_import and has_gltf_loader_var and has_load_function
        print_test("GLTF Loader Integration", passed, 
                  f"Import: {has_gltf_import}, Variable: {has_gltf_loader_var}, Function: {has_load_function}")
        return passed
    except Exception as e:
        print_test("GLTF Loader Integration", False, f"Error: {str(e)}")
        return False

def test_blueprints_registered():
    """Test if all blueprints are registered."""
    try:
        # Test each blueprint's routes
        routes = [
            ("/", "Home"),
            ("/register", "Auth Blueprint"),
            ("/login", "Auth Blueprint"),
            ("/orders/catalog", "Orders Blueprint"),
            ("/dashboard", "Designs Blueprint (requires auth)"),
        ]
        
        all_passed = True
        for route, name in routes:
            response = requests.get(f"{BASE_URL}{route}", allow_redirects=False)
            # 200 = success, 302 = redirect (auth required), both are valid
            passed = response.status_code in [200, 302]
            if not passed:
                all_passed = False
            print(f"      {name}: {response.status_code}")
        
        print_test("Blueprint Registration", all_passed, "All blueprints accessible")
        return all_passed
    except Exception as e:
        print_test("Blueprint Registration", False, f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and display summary."""
    print("\n" + "="*70)
    print(f"{Colors.BLUE}GRUHA ALANKARA - COMPREHENSIVE FEATURE TEST{Colors.END}")
    print(f"Testing at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    tests = [
        ("Core Pages", [
            test_home_page,
            test_catalog_page,
            test_registration_page,
            test_login_page,
        ]),
        ("API Endpoints", [
            test_api_models_endpoint,
        ]),
        ("Database", [
            test_database_tables,
        ]),
        ("AI Features", [
            test_ai_cache_directory,
        ]),
        ("Frontend Assets", [
            test_static_files,
            test_gltf_loader_import,
        ]),
        ("Backend Architecture", [
            test_blueprints_registered,
        ])
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for category, test_functions in tests:
        print(f"\n{Colors.YELLOW}[{category}]{Colors.END}")
        for test_func in test_functions:
            total_tests += 1
            if test_func():
                passed_tests += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {Colors.GREEN}{passed_tests}{Colors.END}")
    print(f"Failed: {Colors.RED}{total_tests - passed_tests}{Colors.END}")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED! Application is ready.{Colors.END}")
    elif success_rate >= 80:
        print(f"\n{Colors.YELLOW}⚠️  Most tests passed. Check failed tests above.{Colors.END}")
    else:
        print(f"\n{Colors.RED}❌ Multiple tests failed. Review implementation.{Colors.END}")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()
