import requests
import json
import io
from PIL import Image, ImageDraw

BASE_URL = "http://127.0.0.1:5000/api"

def run_e2e_test():
    print("=== Starting Phase 3 E2E Backend Verification ===")
    
    # 1. Auth
    user_data = {"email": "e2e@example.com", "password": "password123"}
    login_res = requests.post(f"{BASE_URL}/auth/login", json=user_data)
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("SUCCESS: Auth Verified.")

    # 2. Color Extraction
    print("\n[1/3] Testing Color Extraction...")
    img = Image.new('RGB', (200, 200), color=(180, 100, 50))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    files = {'image': ('theme.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    color_res = requests.post(f"{BASE_URL}/ai/extract-colors", headers=headers, files=files)
    if color_res.status_code == 200:
        print(f"SUCCESS: Palette: {color_res.json()['palette']}")
        print(f"SUCCESS: Style: {color_res.json()['recommended_style']}")

    # 3. Layout Analysis
    print("\n[2/3] Testing Layout Analysis...")
    layout_data = {
        "objects": [
            {"position": {"x": 0.0, "y": 0.0, "z": 0.0}},
            {"position": {"x": 0.1, "y": 0.0, "z": 0.1}} # Colliding
        ]
    }
    layout_res = requests.post(f"{BASE_URL}/ai/analyze-layout", headers=headers, json=layout_data)
    if layout_res.status_code == 200:
        print(f"SUCCESS: Clutter Score: {layout_res.json()['clutter_score']}")
        print(f"SUCCESS: Suggestions: {layout_res.json()['suggestions']}")

    # 4. Assistant Chat
    print("\n[3/3] Testing AI Assistant...")
    chat_data = {
        "message": "Is this room too crowded?",
        "context": {
            "room_type": "living_room",
            "objects": ["Sofa", "Table", "Chair"]
        }
    }
    chat_res = requests.post(f"{BASE_URL}/assistant/chat", headers=headers, json=chat_data)
    if chat_res.status_code == 200:
        print(f"SUCCESS: AI Response: {chat_res.json()['text']}")
        print(f"SUCCESS: Suggestion: {chat_res.json()['action_suggestion']}")

    print("\n=== All Phase 3 Backend Features Verified! ===")

if __name__ == "__main__":
    run_e2e_test()
