import requests
from PIL import Image
import io
import os

BASE_URL = "http://127.0.0.1:5000/api"

def test_ai_flow():
    # 1. Login to get token
    # (Assuming the test user exists or we create one)
    auth_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Try to register first just in case
    requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Test User",
        "email": auth_data["email"],
        "password": auth_data["password"]
    })
    
    print("Logging in...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json=auth_data)
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create a dummy test image
    print("Creating test image...")
    img = Image.new('RGB', (800, 600), color=(73, 109, 137))
    # Add a simple rectangle to simulate an object
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    d.rectangle([100, 100, 400, 400], fill=(200, 100, 100))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    # 3. Call AI Analysis
    print("Calling AI Analyze-Room...")
    files = {'image': ('test.jpg', img_byte_arr, 'image/jpeg')}
    ai_res = requests.post(f"{BASE_URL}/ai/analyze-room", headers=headers, files=files)
    
    if ai_res.status_code == 200:
        print("Success!")
        print(ai_res.json())
    else:
        print(f"AI Analysis failed ({ai_res.status_code}): {ai_res.text}")

if __name__ == "__main__":
    test_ai_flow()
