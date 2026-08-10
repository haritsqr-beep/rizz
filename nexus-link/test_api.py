"""Quick test of NeXuS-LinK API"""
import requests
import json
import time

time.sleep(1)

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("NeXuS-LinK API Test")
print("=" * 60)

# Test 1: Version
print("\n[TEST 1] /api/version")
try:
    r = requests.get(f"{BASE_URL}/api/version")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 2: Search
print("\n[TEST 2] /api/search (POST)")
try:
    payload = {
        "query": "+14155550123",
        "type": "phone",
        "auto_confirm": False
    }
    r = requests.post(f"{BASE_URL}/api/search", json=payload)
    print(f"  Status: {r.status_code}")
    result = r.json()
    print(f"  Search ID: {result.get('search_id')}")
    print(f"  Hits found: {result.get('hit_count')}")
    
    search_id = result.get('search_id')
    if result.get('hits'):
        first_hit = result['hits'][0]
        print(f"  First hit: {first_hit['match']} @ {first_hit['platform']}")
        hit_id = first_hit.get('hit_id') or 'unknown'
        
        # Test 3: Get refinement questions
        print(f"\n[TEST 3] /api/refinement-questions/{hit_id}")
        r3 = requests.get(f"{BASE_URL}/api/refinement-questions/{hit_id}")
        print(f"  Status: {r3.status_code}")
        if r3.status_code == 200:
            questions = r3.json()
            print(f"  Questions: {len(questions.get('questions', []))} generated")
            if questions.get('questions'):
                print(f"  Example: {questions['questions'][0].get('question')}")
        
        # Test 4: Confirm hit
        print(f"\n[TEST 4] /api/confirm (POST)")
        confirm_payload = {
            "search_id": search_id,
            "hit_id": hit_id,
            "answers": {
                "name_match": "yes",
                "age_match": "maybe",
                "location_match": "yes"
            },
            "notes": "Test confirmation"
        }
        r4 = requests.post(f"{BASE_URL}/api/confirm", json=confirm_payload)
        print(f"  Status: {r4.status_code}")
        if r4.status_code == 200:
            confirm_result = r4.json()
            print(f"  Category: {confirm_result.get('category')}")
            print(f"  Confidence: {confirm_result.get('confidence'):.1f}%")
        
        # Test 5: Get results
        print(f"\n[TEST 5] /api/results/{search_id}")
        r5 = requests.get(f"{BASE_URL}/api/results/{search_id}")
        print(f"  Status: {r5.status_code}")
        if r5.status_code == 200:
            results = r5.json()
            print(f"  Overall confidence: {results.get('overall_confidence'):.1f}%")
            print(f"  Confirmed: {results.get('confirmed_count')}")
            print(f"  Potential: {results.get('potential_count')}")

except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
