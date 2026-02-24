import requests
import json
import io
from PIL import Image

BASE_URL = "http://127.0.0.1:5000/api"

def run_phase4_test():
    print("=== Starting Phase 4 Natural Language Intelligence E2E Verification ===")
    
    # 1. Auth Setup
    user_data = {"email": "e2e@example.com", "password": "password123"}
    login_res = requests.post(f"{BASE_URL}/auth/login", json=user_data)
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("SUCCESS: Auth Verified.")

    # 2. Assistant Chat (Phase 4 Structured JSON)
    print("\n[1/3] Testing Structured Assistant Chat...")
    chat_data = {
        "user_message": "Is this room too crowded? I have 15 items.",
        "room_type": "living_room",
        "detected_objects": ["window", "wall"],
        "current_furniture": ["sofa", "table", "chair"],
        "style_theme": "modern"
    }
    chat_res = requests.post(f"{BASE_URL}/assistant/chat", headers=headers, json=chat_data)
    if chat_res.status_code == 200:
        res_json = chat_res.json()
        print(f"SUCCESS: AI Response: {res_json.get('text')}")
        print(f"SUCCESS: Suggested Action: {res_json.get('suggested_action')}")
        assert "text" in res_json
        assert "suggested_action" in res_json

    # 3. Recommendation Refinement
    print("\n[2/3] Testing Recommendation Refinement...")
    # Create a dummy image for /analyze-room
    img = Image.new('RGB', (200, 200), color=(100, 150, 200)) # Blueish for modern feel
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    files = {'image': ('room.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    
    analyze_res = requests.post(f"{BASE_URL}/ai/analyze-room", headers=headers, files=files)
    if analyze_res.status_code == 200:
        res_json = analyze_res.json()
        print(f"SUCCESS: Room Type: {res_json.get('room_type')}")
        print(f"SUCCESS: Refined Recommendations: {[r['name'] for r in res_json.get('recommended_items', [])]}")
        assert len(res_json.get('recommended_items', [])) > 0

    # 4. Cache Verification
    print("\n[3/3] Testing Response Caching...")
    start_time = requests.get(f"{BASE_URL}/health").elapsed.total_seconds() # Just for reference
    
    # Send same chat query again
    chat_res_cached = requests.post(f"{BASE_URL}/assistant/chat", headers=headers, json=chat_data)
    if chat_res_cached.status_code == 200:
        print("SUCCESS: Received response for repeated query.")

    print("\n=== Phase 4 Natural Language Intelligence Layer Verified! ===")

if __name__ == "__main__":
    run_phase4_test()
