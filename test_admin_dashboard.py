"""
Test script to verify admin dashboard endpoints are working correctly.
Run this after starting the Flask backend to diagnose issues.
"""

import requests
import json
from pathlib import Path

# Configuration
BACKEND_URL = 'http://localhost:5000'
API_BASE = f'{BACKEND_URL}/api'

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{BLUE}{'='*60}")
    print(f" {title}")
    print(f"{'='*60}{END}\n")

def print_success(message):
    """Print success message"""
    print(f"{GREEN}✓ {message}{END}")

def print_error(message):
    """Print error message"""
    print(f"{RED}✗ {message}{END}")

def print_warning(message):
    """Print warning message"""
    print(f"{YELLOW}⚠ {message}{END}")

def print_info(message):
    """Print info message"""
    print(f"{BLUE}ℹ {message}{END}")

def check_backend_running():
    """Check if backend is running"""
    print_section("1. BACKEND CONNECTIVITY")
    try:
        response = requests.get(f'{BACKEND_URL}/api/debug/test', timeout=5)
        if response.status_code == 200:
            print_success("Backend is running on port 5000")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend on http://localhost:5000")
        print_info("Make sure Flask app is running: python backend/app.py")
        return False
    except Exception as e:
        print_error(f"Error connecting to backend: {e}")
        return False

def check_model_file():
    """Check if model file exists"""
    print_section("2. MODEL FILE CHECK")
    model_path = Path('backend/models/job_role_rf_enhanced.pkl')
    if model_path.exists():
        size = model_path.stat().st_size
        print_success(f"Model file exists at {model_path}")
        print_info(f"File size: {size / (1024*1024):.2f} MB")
        return True
    else:
        print_error(f"Model file not found at {model_path}")
        return False

def check_data_files():
    """Check if data files exist"""
    print_section("3. DATA FILES CHECK")
    data_files = [
        'data/preprocessed_data.csv',
        'data/original_dataset.csv',
        'backend/processed_data.csv'
    ]
    all_exist = True
    for file_path in data_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size / 1024  # KB
            print_success(f"Found: {file_path} ({size:.1f} KB)")
        else:
            print_error(f"Missing: {file_path}")
            all_exist = False
    return all_exist

def test_model_metrics_endpoint():
    """Test /api/admin/model-metrics endpoint"""
    print_section("4. MODEL METRICS ENDPOINT TEST")
    
    # First, get an auth token
    print_info("Attempting to test without authentication first...")
    try:
        response = requests.get(f'{API_BASE}/admin/model-metrics', timeout=5)
        
        if response.status_code == 401:
            print_warning("Authentication required (401) - Need valid JWT token")
            print_info("To test this endpoint, you need to:")
            print_info("1. Log in as an admin user")
            print_info("2. Copy the JWT token from localStorage")
            print_info("3. Run: curl -H 'Authorization: Bearer <token>' http://localhost:5000/api/admin/model-metrics")
            return None
        elif response.status_code == 403:
            print_error("Access forbidden (403) - User is not admin")
            return False
        elif response.status_code == 200:
            data = response.json()
            print_success("Endpoint returned 200 OK")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    except Exception as e:
        print_error(f"Error testing endpoint: {e}")
        return False

def test_dataset_stats_endpoint():
    """Test /api/admin/dataset-stats endpoint"""
    print_section("5. DATASET STATS ENDPOINT TEST")
    
    print_info("Attempting to test without authentication first...")
    try:
        response = requests.get(f'{API_BASE}/admin/dataset-stats', timeout=5)
        
        if response.status_code == 401:
            print_warning("Authentication required (401) - Need valid JWT token")
            return None
        elif response.status_code == 403:
            print_error("Access forbidden (403) - User is not admin")
            return False
        elif response.status_code == 200:
            data = response.json()
            print_success("Endpoint returned 200 OK")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if response has expected structure
            if 'success' in data and 'total' in data and 'roles' in data:
                print_success("Response has correct structure")
                if data['roles']:
                    print_info(f"Found {len(data['roles'])} job role predictions in database")
                    for role in data['roles'][:3]:
                        print_info(f"  - {role['job_role']}: {role['count']} predictions ({role['percentage']}%)")
                else:
                    print_warning("No predictions found in database yet - Dataset is empty")
                return True
            else:
                print_error("Response missing expected fields")
                return False
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    except Exception as e:
        print_error(f"Error testing endpoint: {e}")
        return False

def check_database():
    """Check if database has predictions"""
    print_section("6. DATABASE CHECK")
    try:
        from backend.models import db, Prediction
        from backend.app import app
        
        with app.app_context():
            prediction_count = db.session.query(Prediction).count()
            if prediction_count > 0:
                print_success(f"Database has {prediction_count} predictions")
                
                # Get role distribution
                from sqlalchemy import func
                roles = db.session.query(
                    Prediction.job_role, 
                    func.count(Prediction.id)
                ).group_by(Prediction.job_role).all()
                
                print_info(f"Job roles in database: {len(roles)}")
                for role, count in roles[:5]:
                    print_info(f"  - {role}: {count} predictions")
                return True
            else:
                print_warning("Database has no predictions yet")
                print_info("Make test predictions through the app to populate data")
                return False
    except ImportError:
        print_warning("Cannot import Flask app - Skipping database check")
        print_info("Run this script from the project root directory")
        return None
    except Exception as e:
        print_error(f"Database check error: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print(f"\n{BLUE}{'='*60}")
    print(" ADMIN DASHBOARD DIAGNOSTICS")
    print(f"{'='*60}{END}\n")
    
    print(f"{BLUE}Backend URL: {BACKEND_URL}{END}")
    print(f"{BLUE}API Base: {API_BASE}{END}\n")
    
    # Run checks
    results = []
    
    results.append(("Backend Running", check_backend_running()))
    if results[-1][1]:  # Only continue if backend is running
        results.append(("Model File", check_model_file()))
        results.append(("Data Files", check_data_files()))
        results.append(("Model Metrics Endpoint", test_model_metrics_endpoint()))
        results.append(("Dataset Stats Endpoint", test_dataset_stats_endpoint()))
        results.append(("Database Check", check_database()))
    
    # Print summary
    print_section("SUMMARY")
    for check_name, result in results:
        if result is True:
            print_success(f"{check_name} - PASS")
        elif result is False:
            print_error(f"{check_name} - FAIL")
        elif result is None:
            print_warning(f"{check_name} - SKIPPED")
    
    # Overall recommendation
    print_section("NEXT STEPS")
    
    backend_ok = results[0][1]
    if not backend_ok:
        print_error("Backend is not running!")
        print_info("Start the backend with: cd backend && python app.py")
    else:
        predictions_empty = any(
            check_name == "Database Check" and result is False 
            for check_name, result in results
        )
        
        if predictions_empty:
            print_warning("Database has no predictions yet")
            print_info("The dataset stats will show empty until predictions are made:")
            print_info("1. Log in as a user")
            print_info("2. Fill in education details")
            print_info("3. Get a job role prediction")
            print_info("4. Return to admin dashboard")
        
        print_info("\nTo fully test the admin dashboard:")
        print_info("1. Open admin.html in browser")
        print_info("2. Log in as an admin user")
        print_info("3. Open DevTools (F12) → Network tab")
        print_info("4. Check if /api/admin/model-metrics requests succeed")
        print_info("5. Check if /api/admin/dataset-stats requests succeed")
        print_info("6. Look for any error messages in Console tab")

if __name__ == '__main__':
    main()
