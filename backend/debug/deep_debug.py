"""
Test the actual API endpoint to see what's different
"""

import requests
import json

# The EXACT code from your test
bubble_sort_code = """arr = [64, 34, 25, 12, 22]
n = len(arr)
for i in range(n):
    for j in range(0, n-i-1):
        if arr[j] > arr[j+1]:
            arr[j], arr[j+1] = arr[j+1], arr[j]"""

print("=" * 80)
print("TESTING ACTUAL API ENDPOINT")
print("=" * 80)

print(f"\n📝 Code being sent:")
print(f"   Length: {len(bubble_sort_code)}")
print(f"   First 100 chars: {repr(bubble_sort_code[:100])}")
print(f"   Has newlines: {chr(10) in bubble_sort_code}")

# Make API request
url = "http://localhost:8000/visualize"
payload = {
    "code": bubble_sort_code,
    "language": "python"
}

print(f"\n🌐 Calling API: {url}")

try:
    response = requests.post(url, json=payload)
    
    print(f"\n✅ Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n📊 API returned:")
        print(f"   Success: {result.get('success')}")
        print(f"   Total steps: {result.get('total_steps')}")
        print(f"   Analyzer: {result.get('analyzer')}")
        
        if result.get('total_steps') == 2:
            print("\n❌ BUG CONFIRMED IN API!")
            print("   The API is returning only 2 steps")
            print("\n   First 2 steps:")
            for i, step in enumerate(result.get('steps', [])[:2]):
                print(f"\n   Step {i}:")
                print(f"     Code: {step.get('code')}")
                print(f"     Viz type: {step.get('visualization', {}).get('type')}")
                print(f"     Viz op: {step.get('visualization', {}).get('operation')}")
        
        elif result.get('total_steps') == 25:
            print("\n✅ API WORKS! Returns 25 steps")
            print("   The problem was fixed!")
        
        elif result.get('total_steps') == 42:
            print("\n✅ API WORKS! Returns 42 steps (universal_visualizer)")
            print("   code_analyzer was skipped, but visualization works!")
        
        else:
            print(f"\n⚠️ UNEXPECTED: Got {result.get('total_steps')} steps")
    
    else:
        print(f"\n❌ API Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to API")
    print("   Make sure the API is running: python main.py")
    print("   Or: uvicorn main:app --reload")

except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "=" * 80)