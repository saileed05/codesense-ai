"""
Fixed Universal Code Visualizer - Handles Sorting Better
"""

import sys
import ast
import json
import traceback
from typing import Any, Dict, List
from collections import deque


class UniversalCodeTracer:
    """Traces any Python code execution and generates visualization steps"""
    
    def __init__(self, code: str):
        self.code = code
        self.steps = []
        self.current_line = 0
        self.local_vars = {}
        self.previous_vars = {}
        self.call_stack = []
        self.skip_initial_assignments = True
        self.step_count = 0
        
    def trace_execution(self, frame, event, arg):
        """Trace callback for sys.settrace"""
        if event == 'line':
            self.current_line = frame.f_lineno
            self.local_vars = frame.f_locals.copy()
            
            # Get the actual code line
            code_lines = self.code.split('\n')
            if 0 <= self.current_line - 1 < len(code_lines):
                code_line = code_lines[self.current_line - 1].strip()
            else:
                code_line = ""
            
            # Skip if we're still in initial variable setup (first 3 lines)
            self.step_count += 1
            if self.step_count <= 3 and not any(keyword in code_line for keyword in ['for', 'while', 'if']):
                self.previous_vars = self.local_vars.copy()
                return self.trace_execution
            
            # Generate visualization for current state
            step = {
                'line': self.current_line,
                'code': code_line,
                'description': self.generate_description(code_line),
                'visualization': self.detect_and_visualize()
            }
            
            self.steps.append(step)
            self.previous_vars = self.local_vars.copy()
            
        elif event == 'call':
            func_name = frame.f_code.co_name
            if func_name not in ['<module>', '<listcomp>', '<dictcomp>']:
                self.call_stack.append(func_name)
                
        elif event == 'return':
            if self.call_stack:
                self.call_stack.pop()
        
        return self.trace_execution
    
    def detect_and_visualize(self) -> Dict:
        """Automatically detect data structures and create visualizations"""
        
        # Priority 1: Detect algorithm-specific structures first
        viz = self.detect_algorithm_pattern()
        if viz:
            return viz
        
        # Priority 2: Show arrays being modified
        for name in ['arr', 'nums', 'array', 'list']:
            if name in self.local_vars:
                value = self.local_vars[name]
                if isinstance(value, list):
                    return self.visualize_list(name, value)
        
        # Priority 3: Show the most "interesting" variable
        for name, value in self.local_vars.items():
            # Skip internal variables and functions
            if name.startswith('_') or callable(value):
                continue
            
            # Detect data structure type
            if isinstance(value, list):
                return self.visualize_list(name, value)
            
            elif isinstance(value, dict):
                # Check if it's a graph
                if self.is_graph(value):
                    return self.visualize_graph(name, value)
                else:
                    return self.visualize_dict(name, value)
            
            elif isinstance(value, (set, frozenset)):
                return self.visualize_set(name, value)
            
            elif isinstance(value, deque):
                return self.visualize_queue(name, value)
        
        # Priority 4: Show simple variables if nothing else
        for name, value in self.local_vars.items():
            if not name.startswith('_') and isinstance(value, (int, float, str, bool)):
                return self.visualize_variable(name, value)
        
        return {'type': 'none', 'message': 'No variables to visualize'}
    
    def detect_algorithm_pattern(self) -> Dict:
        """Detect common algorithm patterns (BFS, DFS, sorting, etc.)"""
        
        # Check for BFS pattern: queue + visited + graph
        if self.has_variables(['queue', 'visited', 'graph']):
            return self.visualize_bfs()
        
        # Check for DFS pattern: stack + visited + graph
        if self.has_variables(['stack', 'visited', 'graph']):
            return self.visualize_dfs()
        
        # Check for sorting: array with i and j indices
        for arr_name in ['arr', 'nums', 'array']:
            if arr_name in self.local_vars:
                arr = self.local_vars[arr_name]
                if isinstance(arr, list) and len(arr) > 0:
                    # Check if we have loop indices
                    if 'i' in self.local_vars or 'j' in self.local_vars:
                        return self.visualize_sorting(arr_name)
        
        return None
    
    def has_variables(self, var_names: List[str]) -> bool:
        """Check if all variable names exist"""
        return all(name in self.local_vars for name in var_names)
    
    def is_graph(self, value: dict) -> bool:
        """Check if dict represents a graph (adjacency list)"""
        if not value:
            return False
        # Graph: all values are lists/sets
        return all(isinstance(v, (list, set)) for v in value.values())
    
    # ==================== VISUALIZATION METHODS ====================
    
    def visualize_sorting(self, arr_name: str) -> Dict:
        """Visualize sorting algorithms with proper highlighting"""
        arr = self.local_vars.get(arr_name, [])
        i = self.local_vars.get('i', -1)
        j = self.local_vars.get('j', -1)
        
        highlight = []
        operation = None
        
        # Determine what operation is happening
        if j >= 0 and j < len(arr):
            highlight.append(j)
            if j + 1 < len(arr):
                highlight.append(j + 1)
            operation = 'comparing'
        elif i >= 0 and i < len(arr):
            highlight.append(i)
            operation = 'iteration'
        
        return {
            'type': 'array',
            'name': arr_name,
            'data': arr,
            'capacity': len(arr),
            'highlight': highlight,
            'operation': operation
        }
    
    def visualize_bfs(self) -> Dict:
        """Visualize BFS algorithm"""
        queue = self.local_vars.get('queue', deque())
        visited = self.local_vars.get('visited', set())
        graph = self.local_vars.get('graph', {})
        current = self.local_vars.get('current', None)
        
        return {
            'type': 'graph_with_ds',
            'graph': {
                'name': 'Graph',
                'nodes': list(graph.keys()),
                'edges': graph,
                'positions': self.generate_positions(list(graph.keys())),
                'current_node': current,
                'visited': list(visited),
                'exploring': []
            },
            'data_structure': {
                'type': 'queue',
                'name': 'queue',
                'data': list(queue),
                'highlight': [len(queue) - 1] if queue else [],
                'operation': 'processing'
            }
        }
    
    def visualize_dfs(self) -> Dict:
        """Visualize DFS algorithm"""
        stack = self.local_vars.get('stack', [])
        visited = self.local_vars.get('visited', set())
        graph = self.local_vars.get('graph', {})
        current = self.local_vars.get('current', None)
        
        return {
            'type': 'graph_with_ds',
            'graph': {
                'name': 'Graph',
                'nodes': list(graph.keys()),
                'edges': graph,
                'positions': self.generate_positions(list(graph.keys())),
                'current_node': current,
                'visited': list(visited),
                'exploring': []
            },
            'data_structure': {
                'type': 'stack',
                'name': 'stack',
                'data': stack,
                'highlight': [len(stack) - 1] if stack else [],
                'operation': 'processing'
            }
        }
    
    def visualize_list(self, name: str, value: list) -> Dict:
        """Visualize list/array"""
        # Try to detect if there's an active index
        highlight = []
        i = self.local_vars.get('i', -1)
        j = self.local_vars.get('j', -1)
        
        if i >= 0 and i < len(value):
            highlight.append(i)
        if j >= 0 and j < len(value) and j != i:
            highlight.append(j)
        
        return {
            'type': 'array',
            'name': name,
            'data': value,
            'capacity': len(value),
            'highlight': highlight,
            'operation': None
        }
    
    def visualize_graph(self, name: str, value: dict) -> Dict:
        """Visualize graph structure"""
        nodes = list(value.keys())
        return {
            'type': 'graph',
            'name': name,
            'nodes': nodes,
            'edges': value,
            'formatted': [f"{node} -> {', '.join(map(str, neighbors))}" 
                         for node, neighbors in value.items()]
        }
    
    def visualize_dict(self, name: str, value: dict) -> Dict:
        """Visualize dictionary"""
        formatted = []
        for k, v in value.items():
            formatted.append(f"{k}: {v}")
        
        return {
            'type': 'dict',
            'name': name,
            'data': value,
            'formatted': formatted
        }
    
    def visualize_set(self, name: str, value: set) -> Dict:
        """Visualize set as visited tracker"""
        return {
            'type': 'visited',
            'name': name,
            'data': list(value),
            'highlight': []
        }
    
    def visualize_queue(self, name: str, value: deque) -> Dict:
        """Visualize queue"""
        return {
            'type': 'queue',
            'name': name,
            'data': list(value),
            'highlight': [],
            'operation': None
        }
    
    def visualize_variable(self, name: str, value: Any) -> Dict:
        """Visualize simple variable with proper value display"""
        # Properly evaluate and display the value
        if isinstance(value, (int, float)):
            display_value = str(value)
        elif isinstance(value, str):
            display_value = f'"{value}"'
        elif isinstance(value, bool):
            display_value = str(value)
        elif value is None:
            display_value = "None"
        else:
            display_value = str(value)
        
        return {
            'type': 'variable',
            'name': name,
            'value': display_value,
            'var_type': type(value).__name__
        }
    
    def generate_positions(self, nodes: List) -> Dict:
        """Generate circular positions for graph nodes"""
        import math
        n = len(nodes)
        positions = {}
        
        radius = 180
        center_x, center_y = 400, 250
        
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions[node] = {'x': int(x), 'y': int(y)}
        
        return positions
    
    def generate_description(self, code_line: str) -> str:
        """Generate natural language description of code line"""
        code_line = code_line.strip()
        
        if not code_line:
            return "Executing code..."
        
        # Get current variable values for better descriptions
        i = self.local_vars.get('i', None)
        j = self.local_vars.get('j', None)
        n = self.local_vars.get('n', None)
        
        if code_line.startswith('def '):
            return "Defining function"
        elif code_line.startswith('n ='):
            return "Getting array length"
        elif code_line.startswith('for i in range'):
            return f"Starting outer loop (i = {i})" if i is not None else "Starting outer loop"
        elif code_line.startswith('for j in range'):
            return f"Starting inner loop (j = {j})" if j is not None else "Starting inner loop"
        elif 'if arr[j] > arr[j+1]' in code_line or 'if arr[j] > arr[j + 1]' in code_line:
            return f"Comparing elements at positions {j} and {j+1}" if j is not None else "Comparing adjacent elements"
        elif 'arr[j], arr[j+1]' in code_line or 'arr[j], arr[j + 1]' in code_line:
            return f"Swapping elements at positions {j} and {j+1}" if j is not None else "Swapping elements"
        elif '=' in code_line and 'if' not in code_line:
            var_name = code_line.split('=')[0].strip()
            return f"Setting {var_name}"
        elif 'append' in code_line:
            return "Adding element to list"
        elif 'pop' in code_line:
            return "Removing element"
        elif 'print' in code_line:
            return "Printing output"
        else:
            return f"Executing: {code_line[:50]}"
    
    def execute(self, max_steps: int = 100) -> Dict:
        """Execute code with tracing"""
        try:
            # Create execution namespace
            exec_globals = {
                '__builtins__': __builtins__,
                'deque': deque,
            }
            
            # Set up tracing
            sys.settrace(self.trace_execution)
            
            # Execute code
            exec(self.code, exec_globals)
            
            # Stop tracing
            sys.settrace(None)
            
            # Limit steps to prevent overwhelming UI
            if len(self.steps) > max_steps:
                self.steps = self.steps[:max_steps]
                self.steps.append({
                    'line': 0,
                    'code': '...',
                    'description': f'Showing first {max_steps} steps only',
                    'visualization': {'type': 'none', 'message': 'Execution continues...'}
                })
            
            return {
                'success': True,
                'steps': self.steps,
                'total_steps': len(self.steps)
            }
            
        except Exception as e:
            sys.settrace(None)
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'steps': self.steps  # Return partial steps
            }


# ==================== TEST CODE ====================

if __name__ == "__main__":
    # Test with Bubble Sort
    bubble_sort_code = """
arr = [64, 34, 25, 12, 22, 11, 90]

n = len(arr)
for i in range(n):
    for j in range(0, n-i-1):
        if arr[j] > arr[j+1]:
            arr[j], arr[j+1] = arr[j+1], arr[j]
"""
    
    print("Testing Bubble Sort Visualization...")
    tracer = UniversalCodeTracer(bubble_sort_code)
    result = tracer.execute(max_steps=50)
    
    if result['success']:
        print(f"✅ Generated {len(result['steps'])} steps")
        print("\nSample steps:")
        for i, step in enumerate(result['steps'][:5]):
            print(f"\nStep {i+1}:")
            print(f"  Line {step['line']}: {step['code']}")
            print(f"  Description: {step['description']}")
            print(f"  Viz type: {step['visualization']['type']}")
            if step['visualization']['type'] == 'array':
                print(f"  Array: {step['visualization']['data']}")
                print(f"  Highlighted: {step['visualization']['highlight']}")
    else:
        print(f"❌ Error: {result['error']}")