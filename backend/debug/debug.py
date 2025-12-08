# Test script to debug why sorting detection is failing
# Run this to see what's happening

code = """arr = [64, 34, 25, 12, 22]
n = len(arr)
for i in range(n):
    for j in range(0, n-i-1):
        if arr[j] > arr[j+1]:
            arr[j], arr[j+1] = arr[j+1], arr[j]
"""

code_lower = code.lower()

# Check all conditions
has_nested_loops = code_lower.count('for') >= 2
has_range = 'range' in code_lower
has_array_var = any(var in code_lower for var in ['arr', 'array', 'nums', 'list', 'data'])

# Check for swap patterns
has_swap = (
    ('[i]' in code and '[j]' in code) or
    ('[j]' in code and '[j+1]' in code) or
    ('[j]' in code and '[j + 1]' in code)
)

has_comparison = any(op in code for op in ['>', '<', '>=', '<='])

# Detect specific patterns
is_bubble_sort = has_nested_loops and has_swap and '[j+1]' in code
is_selection_sort = has_nested_loops and 'min_idx' in code_lower
is_insertion_sort = (
    has_nested_loops and 
    ('insert' in code_lower or ('key' in code_lower and has_comparison))
)

# Combined detection
is_sorting_algorithm = (
    has_nested_loops and 
    has_range and 
    has_array_var and 
    has_comparison and 
    (is_bubble_sort or is_selection_sort or is_insertion_sort or has_swap)
)

print("=" * 60)
print("SORTING DETECTION DEBUG")
print("=" * 60)
print(f"✅ has_nested_loops: {has_nested_loops} (found {code_lower.count('for')} loops)")
print(f"✅ has_range: {has_range}")
print(f"✅ has_array_var: {has_array_var}")
print(f"✅ has_swap: {has_swap}")
print(f"✅ has_comparison: {has_comparison}")
print()
print(f"Pattern detection:")
print(f"  - is_bubble_sort: {is_bubble_sort}")
print(f"  - is_selection_sort: {is_selection_sort}")
print(f"  - is_insertion_sort: {is_insertion_sort}")
print()
print(f"🎯 FINAL RESULT: is_sorting_algorithm = {is_sorting_algorithm}")
print()

if is_sorting_algorithm:
    print("✅ ✅ ✅ SORTING DETECTED! Should use universal_visualizer")
else:
    print("❌ ❌ ❌ NOT DETECTED AS SORTING! Will use code_analyzer")
    print()
    print("Missing conditions:")
    if not has_nested_loops:
        print("  ❌ Not enough loops")
    if not has_range:
        print("  ❌ No 'range' found")
    if not has_array_var:
        print("  ❌ No array variable")
    if not has_comparison:
        print("  ❌ No comparison operator")
    if not (is_bubble_sort or is_selection_sort or is_insertion_sort or has_swap):
        print("  ❌ No sorting pattern detected")

print("=" * 60)