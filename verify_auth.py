import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_flow():
    # 1. Login
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    print(f"Logging in with {login_data['email']}...")
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if r.status_code != 200:
            print(f"Login failed: {r.status_code} - {r.text}")
            return
        
        token = r.json().get('access_token')
        print("Login successful! Token received.")
        
        # 2. Test Admin API
        headers = {"Authorization": f"Bearer {token}"}
        print("Testing Admin Users list...")
        r = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        
        if r.status_code == 200:
            print("SUCCESS: Admin access granted!")
            print(f"Users found: {len(r.json())}")
        else:
            print(f"FAILED: {r.status_code} - {r.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_flow()
