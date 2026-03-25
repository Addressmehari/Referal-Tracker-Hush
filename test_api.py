import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

def run_test():
    print("🚀 Starting Automated Referral API Test...")
    
    # 1. Register App
    print("\n[1/4] Registering 'Fitness Tracker' App...")
    app_res = requests.post(f"{BASE_URL}/apps", json={"name": "Fitness Tracker"})
    app_data = app_res.json()
    api_key = app_data["api_key"]
    app_id = app_data["id"]
    print(f"✅ App Registered. ID: {app_id}, API_KEY: {api_key}")

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    # 2. Register Alice and get her code
    print("\n[2/4] Generating referral code for Alice...")
    u1_res = requests.post(f"{BASE_URL}/users/generate-code", headers=headers, json={"external_user_id": "alice_01"})
    alice_data = u1_res.json()
    alice_code = alice_data["referral_code"]
    print(f"✅ Alice (alice_01) code: {alice_code}")

    # 3. Bob joins using Alice's code
    print(f"\n[3/4] Tracking referral: Bob signs up using code {alice_code}...")
    track_res = requests.post(f"{BASE_URL}/referrals/track", headers=headers, json={
        "referee_id": "bob_99", 
        "referral_code": alice_code
    })
    print(f"✅ Bob registered. API Response: {track_res.text}")

    # 4. Charlie joins using Bob's code (to test nesting)
    # First get Bob's code
    bob_res = requests.post(f"{BASE_URL}/users/generate-code", headers=headers, json={"external_user_id": "bob_99"})
    bob_code = bob_res.json()["referral_code"]
    
    print(f"\n[4/4] Tracking nested referral: Charlie signs up using Bob's code {bob_code}...")
    track_c_res = requests.post(f"{BASE_URL}/referrals/track", headers=headers, json={
        "referee_id": "charlie_777",
        "referral_code": bob_code
    })
    print(f"✅ Charlie registered. API Response: {track_c_res.text}")

    # 5. Verify the tree
    print("\n📊 Fetching final Referral Tree...")
    tree_res = requests.get(f"{BASE_URL}/apps/{app_id}/tree")
    print(json.dumps(tree_res.json(), indent=2))
    
    print("\n✨ Test Complete. You can also view this tree at http://localhost:8000 by entering App ID:", app_id)

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("💡 Make sure uvicorn is running on http://localhost:8000")
