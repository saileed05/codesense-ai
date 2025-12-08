"""
Test script to diagnose sorting detection issues
Run this to see what's happening with code_analyzer vs universal_visualizer
"""

# Import your modules
from code_analyzer import generate_execution_steps, SortingDetector
from universal_visualizer import UniversalCodeTracer

# Your bubble sort code
bubble_sort_code = """arr = [64, 34, 25, 12, 22]
n = len(arr)
for i in range(n):
    for j in range(0, n-i-1):
        if arr[j] > arr[j+1]:
            arr[j], arr[j+1] = arr[j+1], arr[j]"""

print("=" * 80)
print("TEST 1: SortingDetector")
print("=" * 80)

detector = SortingDetector(bubble_sort_code)
algorithm = detector.detect_sorting()
arr = detector.extract_array()

print(f"✅ Detected algorithm: {algorithm}")
print(f"✅ Extracted array: {arr}")

print("\n" + "=" * 80)
print("TEST 2: code_analyzer (generate_execution_steps)")
print("=" * 80)

steps_from_analyzer = generate_execution_steps(bubble_sort_code, "python")
print(f"📊 code_analyzer returned: {len(steps_from_analyzer)} steps")

if len(steps_from_analyzer) <= 5:
    print("⚠️ WARNING: Only got initialization steps!")
    print("\nFirst 5 steps:")
    for i, step in enumerate(steps_from_analyzer[:5]):
        print(f"\nStep {i}:")
        print(f"  Code: {step.get('code', 'N/A')}")
        print(f"  Description: {step.get('description', 'N/A')}")
        viz = step.get('visualization', {})
        print(f"  Viz Type: {viz.get('type', 'none')}")
        print(f"  Operation: {viz.get('operation', 'none')}")
else:
    print("✅ Got full sorting simulation!")
    
    # Count operation types
    operations = {}
    for step in steps_from_analyzer:
        op = step.get('visualization', {}).get('operation', 'none')
        operations[op] = operations.get(op, 0) + 1
    
    print("\nOperation breakdown:")
    for op, count in operations.items():
        print(f"  {op}: {count} times")

print("\n" + "=" * 80)
print("TEST 3: universal_visualizer")
print("=" * 80)

tracer = UniversalCodeTracer(bubble_sort_code)
result = tracer.execute(max_steps=200)

print(f"📊 universal_visualizer returned: {result['total_steps']} steps")
print(f"✅ Success: {result['success']}")

if result['success']:
    print("\nFirst 5 steps:")
    for i, step in enumerate(result['steps'][:5]):
        print(f"\nStep {i}:")
        print(f"  Line {step['line']}: {step['code']}")
        print(f"  Description: {step['description']}")
        viz = step['visualization']
        print(f"  Viz Type: {viz['type']}")
        if viz['type'] == 'array':
            print(f"  Array data: {viz.get('data', [])}")
            print(f"  Comparing: {viz.get('comparing', [])}")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)

if len(steps_from_analyzer) > 10:
    print("✅ USE code_analyzer - it has detailed sorting simulation")
elif result['success'] and result['total_steps'] > 10:
    print("✅ USE universal_visualizer - it traces actual execution")
else:
    print("❌ BOTH FAILED - check for errors above")