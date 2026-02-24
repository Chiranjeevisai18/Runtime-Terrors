import requests
import json
import io
from PIL import Image, ImageDraw

BASE_URL = "http://127.0.0.1:5000/api"

def run_e2e_test():
    print("=== Starting E2E Backend Verification ===")
    
    # 1. Auth: Register/Login
    user_data = {
        "name": "E2E Tester",
        "email": "e2e@example.com",
        "password": "password123"
    }
    
    print("\n[1/6] Testing Auth...")
    requests.post(f"{BASE_URL}/auth/register", json=user_data) # Ensure user exists
    login_res = requests.post(f"{BASE_URL}/auth/login", json=user_data)
    
    if login_res.status_code != 200:
        print(f"FAILED: Login - {login_res.text}")
        return
    
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("SUCCESS: Logged in and received JWT token.")

    # 2. AI Analysis
    print("\n[2/6] Testing AI Analysis...")
    img = Image.new('RGB', (800, 600), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.rectangle([100, 100, 400, 400], fill=(200, 100, 100)) # Simulating an object
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    files = {'image': ('test.jpg', img_byte_arr, 'image/jpeg')}
    ai_res = requests.post(f"{BASE_URL}/ai/analyze-room", headers=headers, files=files)
    
    if ai_res.status_code != 200:
        print(f"FAILED: AI Analysis - {ai_res.text}")
    else:
        results = ai_res.json()
        print(f"SUCCESS: AI Response: {results['description']}")
        print(f"SUCCESS: Recommendations: {[r['model_id'] for r in results['recommended_items']]}")

    # 3. Save Design
    print("\n[3/6] Testing Design Save...")
    design_data = {
        "name": "E2E Test Design",
        "description": "Test design for reconstruction",
        "objects": [
            {
                "model_id": "modern_sofa",
                "position": {"x": 1.1, "y": 0.0, "z": -2.5},
                "rotation": 45.0,
                "scale": 1.2
            },
            {
                "model_id": "floor_lamp",
                "position": {"x": -0.5, "y": 0.0, "z": -3.0},
                "rotation": 0.0,
                "scale": 1.0
            }
        ]
    }
    save_res = requests.post(f"{BASE_URL}/designs", headers=headers, json=design_data)
    
    if save_res.status_code != 201:
        print(f"FAILED: Save Design - {save_res.text}")
        return
    
    design_id = save_res.json()['id']
    print(f"SUCCESS: Design saved with ID: {design_id}")

    # 4. Fetch All Designs (Sync Test)
    print("\n[4/6] Testing Fetch All Designs...")
    fetch_res = requests.get(f"{BASE_URL}/designs", headers=headers)
    if fetch_res.status_code == 200:
        designs = fetch_res.json()
        print(f"SUCCESS: Found {len(designs)} designs in cloud.")
    else:
        print(f"FAILED: Fetch Designs - {fetch_res.text}")

    # 5. Fetch Design Detail (Reconstruction Test)
    print("\n[5/6] Testing Design Detail (Reconstruction)...")
    detail_res = requests.get(f"{BASE_URL}/designs/{design_id}", headers=headers)
    if detail_res.status_code == 200:
        objects = detail_res.json()['objects']
        print(f"SUCCESS: Reconstructed data has {len(objects)} objects.")
        print(f"SUCCESS: First object scale: {objects[0]['scale']}")
    else:
        print(f"FAILED: Fetch Detail - {detail_res.text}")

    # 6. Delete Design
    print("\n[6/6] Testing Deletion...")
    del_res = requests.delete(f"{BASE_URL}/designs/{design_id}", headers=headers)
    if del_res.status_code == 200:
        print("SUCCESS: Design deleted from cloud.")
    else:
        print(f"FAILED: Delete Design - {del_res.text}")

    print("\n=== E2E Test Completed Successfully ===")

if __name__ == "__main__":
    run_e2e_test()
