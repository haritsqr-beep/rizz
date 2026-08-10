"""Test the new NeXuS-LinK API flow"""
import requests
import json
import time

time.sleep(1)
BASE_URL = "http://localhost:5000"

print("\n" + "="*70)
print("NeXuS-LinK v2.0 - Smart OSINT Search Test")
print("="*70)

# Single search with person profile
print("\n[STEP 1] Search for person:")
print("  Phone: +14155550123")
print("  Email: john@example.com")
print("  Name: John Doe")
print("  Gender: Male")
print("  Age: 35")

payload = {
    "phone": "+14155550123",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "age": 35,
    "gender": "male"
}

try:
    r = requests.post(f"{BASE_URL}/api/search", json=payload)
    print(f"\n[RESPONSE] Status: {r.status_code}")
    
    if r.status_code == 200:
        result = r.json()
        search_id = result.get("search_id")
        
        print(f"\nSearch ID: {search_id}")
        print(f"Summary: {result.get('summary')}")
        print(f"Overall Confidence: {result.get('confidence'):.0%}")
        
        # Show confirmed accounts
        print("\n[CONFIRMED ACCOUNTS] (High confidence match)")
        print("-" * 70)
        confirmed = result.get("confirmed_accounts", [])
        if confirmed:
            for acc in confirmed:
                print(f"  * {acc['name']} @ {acc['platform']}")
                print(f"    Gender: {acc['gender']}, Location: {acc['location']}")
                print(f"    Confidence: {acc['confidence']:.0%}")
                print(f"    URL: {acc['url']}")
                print()
        else:
            print("  (No confirmed accounts)")
        
        # Show potential/maybe accounts
        print("\n[POTENTIAL ACCOUNTS] (Possibly linked to this person)")
        print("-" * 70)
        potential = result.get("potential_accounts", [])
        if potential:
            for acc in potential:
                print(f"  ? {acc['name']} @ {acc['platform']}")
                print(f"    Gender: {acc['gender']}, Location: {acc['location']}")
                print(f"    Confidence: {acc['confidence']:.0%}")
                print(f"    URL: {acc['url']}")
                print()
        else:
            print("  (No potential accounts)")
        
        # Show dating accounts
        print("\n[DATING SITE PROFILES] (Found on dating platforms)")
        print("-" * 70)
        dating = result.get("dating_accounts", [])
        if dating:
            for acc in dating:
                print(f"  [DATING] {acc['name']} @ {acc['platform']}")
                print(f"    Gender: {acc['gender']}")
                print(f"    Confidence: {acc['confidence']:.0%}")
                print(f"    Note: {acc.get('note', '')}")
                print()
        else:
            print("  (No dating profiles found)")
        
        # Get detailed results
        print("\n[STEP 2] Fetch detailed results:")
        r2 = requests.get(f"{BASE_URL}/api/results/{search_id}")
        if r2.status_code == 200:
            detailed = r2.json()
            print(f"\nTotal Accounts Found: {detailed.get('total_accounts_found')}")
            print(f"Confirmed: {detailed['confirmed_accounts']['count']}")
            print(f"Potential: {detailed['potential_accounts']['count']}")
    else:
        print(f"Error: {r.json()}")

except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "="*70)
print("Test complete!")
print("="*70 + "\n")
