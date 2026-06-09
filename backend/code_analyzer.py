"""
Enhanced Code Analyzer v2.4 - COMPLETE FIX
- Resolves variable references in safe_eval_value
- Handles tuple swaps (a, b = b, a) for sorting
- Handles len() calls in assignments
- Improved BFS detection with queue variable checking
Supports ANY graph algorithm visualization: BFS, DFS, Dijkstra, and generic graphs
"""
import ast
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import deque


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def safe_eval_value(node, variable_states: Dict = None):
    """Safely evaluate AST expressions to get actual values with variable resolution"""
    try:
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.List):
            return [safe_eval_value(elt, variable_states) for elt in node.elts]
        elif isinstance(node, ast.Dict):
            result = {}
            for key, value in zip(node.keys, node.values):
                k = safe_eval_value(key, variable_states)
                v = safe_eval_value(value, variable_states)
                if k is not None:
                    result[k] = v
            return result
        elif isinstance(node, ast.Set):
            return {safe_eval_value(elt, variable_states) for elt in node.elts}
        elif isinstance(node, ast.Tuple):
            return tuple(safe_eval_value(elt, variable_states) for elt in node.elts)
        elif isinstance(node, ast.BinOp):
            left = safe_eval_value(node.left, variable_states)
            right = safe_eval_value(node.right, variable_states)
            if isinstance(node.op, ast.Add):
                return left + right if left is not None and right is not None else None
            elif isinstance(node.op, ast.Sub):
                return left - right if left is not None and right is not None else None
            elif isinstance(node.op, ast.Mult):
                return left * right if left is not None and right is not None else None
            elif isinstance(node.op, ast.Div):
                return left / right if left is not None and right is not None and right != 0 else float('inf')
        elif isinstance(node, ast.UnaryOp):
            operand = safe_eval_value(node.operand, variable_states)
            if isinstance(node.op, ast.USub):
                return -operand if operand is not None else None
            elif isinstance(node.op, ast.UAdd):
                return +operand if operand is not None else None
        elif isinstance(node, ast.Name):
            # ✅ FIX 1: Try to resolve variable references
            if variable_states and node.id in variable_states:
                resolved = variable_states[node.id].get("value")
                if resolved is not None:
                    return resolved
            return f"<var:{node.id}>"
        elif isinstance(node, ast.Subscript):
            # Handle arr[index] access
            if variable_states and isinstance(node.value, ast.Name):
                arr_name = node.value.id
                if arr_name in variable_states:
                    arr_data = variable_states[arr_name].get("data", [])
                    if arr_data and isinstance(arr_data, list):
                        index = safe_eval_value(node.slice, variable_states)
                        if isinstance(index, int) and 0 <= index < len(arr_data):
                            return arr_data[index]
            return "..."
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    except:
        try:
            return ast.unparse(node) if hasattr(ast, 'unparse') else "..."
        except:
            return "..."


def detect_type(node, variable_states: Dict = None) -> str:
    """Detect variable type from AST node with context"""
    if isinstance(node, ast.List):
        return "list"
    elif isinstance(node, ast.Dict):
        return "dict"
    elif isinstance(node, ast.Set):
        return "set"
    elif isinstance(node, ast.Tuple):
        return "tuple"
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, int):
            return "int"
        elif isinstance(node.value, float):
            return "float"
        elif isinstance(node.value, str):
            return "string"
        elif isinstance(node.value, bool):
            return "bool"
        elif node.value is None:
            return "none"
    elif isinstance(node, ast.Call):
        if hasattr(node.func, 'id'):
            func_name = node.func.id
            if func_name in ['list', 'dict', 'set', 'tuple', 'deque']:
                return func_name
            elif func_name == 'len':
                return "int"
    elif isinstance(node, ast.Name):
        if variable_states and node.id in variable_states:
            return variable_states[node.id].get("type", "unknown")
    return "unknown"


def format_dict_for_display(d, max_items=10):
    """Format dictionary for visual display"""
    if not isinstance(d, dict):
        return [str(d)]
    
    items = list(d.items())[:max_items]
    formatted = []
    
    for k, v in items:
        if isinstance(v, list):
            if len(v) == 0:
                v_str = "[]"
            elif len(v) <= 3:
                v_str = f"[{', '.join(map(str, v))}]"
            else:
                v_str = f"[{', '.join(map(str, v[:3]))}... +{len(v)-3} more]"
        elif isinstance(v, dict):
            v_str = f"{{...{len(v)} keys}}"
        else:
            v_str = str(v)
        
        formatted.append(f"  {k}: {v_str}")
    
    if len(d) > max_items:
        formatted.append(f"  ... +{len(d) - max_items} more")
    
    return formatted


# ============================================================================
# GRAPH UTILITIES
# ============================================================================

def calculate_graph_positions(nodes, edges):
    """Calculate optimal positions for graph nodes using circle layout"""
    n = len(nodes)
    if n == 0:
        return {}
    
    center_x, center_y = 400, 250
    
    if n == 1:
        radius = 0
    elif n <= 5:
        radius = 120
    else:
        radius = min(180, 80 + n * 8)
    
    positions = {}
    
    for i, node in enumerate(nodes):
        angle = (2 * math.pi * i) / n - (math.pi / 2)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions[node] = {"x": int(x), "y": int(y)}
    
    return positions


def is_adjacency_list(data) -> bool:
    """Check if data is a valid adjacency list (dict with list values)"""
    if not isinstance(data, dict) or not data:
        return False
    return all(isinstance(v, list) for v in data.values())


def is_edge_list(data) -> bool:
    """Check if data is an edge list (list of tuples/lists)"""
    if not isinstance(data, list) or not data:
        return False
    return all(
        isinstance(item, (tuple, list)) and len(item) >= 2 
        for item in data
    )


def edge_list_to_adjacency_list(edges) -> Dict:
    """Convert edge list to adjacency list"""
    adj_list = {}
    
    for edge in edges:
        if len(edge) < 2:
            continue
        
        u, v = edge[0], edge[1]
        
        if u not in adj_list:
            adj_list[u] = []
        if v not in adj_list:
            adj_list[v] = []
        
        adj_list[u].append(v)
        
        if len(edge) > 2:
            adj_list[u][-1] = (v, edge[2])
    
    return adj_list


# ============================================================================
# GRAPH ALGORITHM DETECTION
# ============================================================================

class GraphDetector:
    """Detects graph structures and algorithms in code"""
    
    def __init__(self, code: str, variable_states: Dict):
        self.code = code
        self.code_lower = code.lower()
        self.states = variable_states
        self.graph_var = None
        self.graph_data = None
        self.algorithm = None
        
    def find_graph(self) -> Optional[Tuple[str, Dict]]:
        """Find any graph structure in variables"""
        
        for name, state in self.states.items():
            if state.get('type') == 'dict':
                data = state.get('data', {})
                if is_adjacency_list(data):
                    self.graph_var = name
                    self.graph_data = data
                    return name, data
        
        for name, state in self.states.items():
            if state.get('type') == 'list':
                data = state.get('data', [])
                if is_edge_list(data):
                    adj_list = edge_list_to_adjacency_list(data)
                    self.graph_var = name
                    self.graph_data = adj_list
                    return name, adj_list
        
        return None, None
    
    def detect_algorithm(self) -> Optional[str]:
        """Detect which graph algorithm is being used"""
        
        if not self.graph_var:
            return None
        
        code = self.code
        code_lower = self.code_lower
        
        if ('heapq' in code or 'priorityqueue' in code_lower or 'heappush' in code):
            if 'distance' in code_lower or 'dist' in code_lower:
                self.algorithm = 'dijkstra'
                return 'dijkstra'
        
        if 'indegree' in code_lower or 'in_degree' in code_lower:
            self.algorithm = 'topological_sort'
            return 'topological_sort'
        
        if 'parent' in code_lower and ('union' in code_lower or 'find' in code_lower):
            self.algorithm = 'union_find'
            return 'union_find'
        
        if 'mst' in code_lower or 'minimum spanning tree' in code_lower:
            if 'heapq' in code or 'priorityqueue' in code_lower:
                self.algorithm = 'prim'
                return 'prim'
        
        # ✅ FIX 3: Improved BFS detection with queue variable checking
        if '.pop(0)' in code or '.popleft()' in code:
            has_queue = any(
                state.get('is_queue') or state.get('type') in ['list', 'deque']
                for name, state in self.states.items()
                if 'queue' in name.lower() or name.lower() in ['q', 'qu']
            )
            if has_queue:
                self.algorithm = 'bfs'
                return 'bfs'
        
        if '.pop()' in code and '.append(' in code:
            self.algorithm = 'dfs'
            return 'dfs'
        
        if 'def ' in code and '(' in code:
            func_names = []
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_names.append(node.name)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if hasattr(node.func, 'id') and node.func.id in func_names:
                            self.algorithm = 'dfs_recursive'
                            return 'dfs_recursive'
            except:
                pass
        
        self.algorithm = 'generic'
        return 'generic'


# ============================================================================
# GRAPH TRAVERSAL SIMULATOR
# ============================================================================

def simulate_graph_traversal(graph_data: Dict, start_node, algorithm: str = "bfs") -> List[Dict]:
    """
    Universal graph traversal simulator
    Supports: BFS, DFS, and generic graph display
    """
    
    edges = graph_data
    nodes = list(edges.keys())
    
    all_nodes = set(nodes)
    for neighbors in edges.values():
        for neighbor in neighbors:
            if isinstance(neighbor, tuple):
                all_nodes.add(neighbor[0])
            else:
                all_nodes.add(neighbor)
    nodes = sorted(list(all_nodes))
    
    if start_node not in nodes:
        start_node = nodes[0] if nodes else None
    
    if start_node is None:
        return []
    
    visited = set()
    structure = [start_node]
    traversal_steps = []
    
    positions = calculate_graph_positions(nodes, edges)
    
    traversal_steps.append({
        "graph": {
            "name": f"{'BFS' if algorithm == 'bfs' else 'DFS'} Traversal",
            "nodes": nodes,
            "edges": edges,
            "positions": positions,
            "current_node": None,
            "visited": [],
            "exploring": []
        },
        "data_structure": {
            "type": "queue" if algorithm == "bfs" else "stack",
            "name": "Queue" if algorithm == "bfs" else "Stack",
            "data": [start_node],
            "highlight": [0],
            "operation": "enqueue" if algorithm == "bfs" else "push"
        }
    })
    
    while structure:
        if algorithm == "bfs":
            current = structure.pop(0)
        else:
            current = structure.pop()
        
        if current in visited:
            continue
        
        visited.add(current)
        
        traversal_steps.append({
            "graph": {
                "name": f"{'BFS' if algorithm == 'bfs' else 'DFS'} Traversal",
                "nodes": nodes,
                "edges": edges,
                "positions": positions,
                "current_node": current,
                "visited": list(visited),
                "exploring": []
            },
            "data_structure": {
                "type": "queue" if algorithm == "bfs" else "stack",
                "name": "Queue" if algorithm == "bfs" else "Stack",
                "data": structure[:],
                "removed_value": current,
                "operation": "dequeue" if algorithm == "bfs" else "pop"
            }
        })
        
        neighbors = edges.get(current, [])
        
        for neighbor in neighbors:
            if isinstance(neighbor, tuple):
                neighbor_node = neighbor[0]
            else:
                neighbor_node = neighbor
            
            if neighbor_node not in visited and neighbor_node not in structure:
                structure.append(neighbor_node)
                
                traversal_steps.append({
                    "graph": {
                        "name": f"{'BFS' if algorithm == 'bfs' else 'DFS'} Traversal",
                        "nodes": nodes,
                        "edges": edges,
                        "positions": positions,
                        "current_node": current,
                        "visited": list(visited),
                        "exploring": [neighbor_node]
                    },
                    "data_structure": {
                        "type": "queue" if algorithm == "bfs" else "stack",
                        "name": "Queue" if algorithm == "bfs" else "Stack",
                        "data": structure[:],
                        "highlight": [len(structure) - 1],
                        "operation": "enqueue" if algorithm == "bfs" else "push"
                    }
                })
    
    traversal_steps.append({
        "graph": {
            "name": f"{'BFS' if algorithm == 'bfs' else 'DFS'} Traversal Complete",
            "nodes": nodes,
            "edges": edges,
            "positions": positions,
            "current_node": None,
            "visited": list(visited),
            "exploring": []
        },
        "data_structure": {
            "type": "queue" if algorithm == "bfs" else "stack",
            "name": "Queue" if algorithm == "bfs" else "Stack",
            "data": [],
            "operation": None
        }
    })
    
    return traversal_steps


# ============================================================================
# MAIN EXECUTION STEP GENERATOR
# ============================================================================

def generate_execution_steps(code: str, language: str = "python") -> List[Dict[str, Any]]:
    """
    Generate step-by-step execution visualization
    ✅ FIXED VERSION: Resolves variables, handles tuple swaps, len() calls, BFS detection
    """
    
    steps = []
    
    if language.lower() != "python":
        return [{
            "step": 0,
            "line": 1,
            "code": f"# {language.upper()} visualization coming soon",
            "description": f"⚠️ Currently only Python is supported. Try Python code with graphs, arrays, stacks, or BFS/DFS!",
            "visualization": {
                "type": "none",
                "message": f"💡 Tip: Supported algorithms include BFS, DFS, Dijkstra, stacks, and basic data structures"
            }
        }]
    
    try:
        lines = code.split('\n')
        tree = ast.parse(code)
        
        step_num = 0
        variable_states = {}
        
        # ===== PHASE 1: Collect all variable assignments WITH METADATA =====
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        var_type = detect_type(node.value)
                        actual_value = safe_eval_value(node.value)
                        
                        # ✅ CRITICAL: Store data structure type metadata
                        is_stack = 'stack' in var_name.lower() or var_name.lower() in ['s', 'st', 'stk']
                        is_queue = 'queue' in var_name.lower() or var_name.lower() in ['q', 'qu']
                        is_visited = 'visited' in var_name.lower() or 'seen' in var_name.lower()
                        
                        variable_states[var_name] = {
                            "type": var_type,
                            "value": actual_value,
                            "data": actual_value if isinstance(actual_value, (list, dict, set)) else None,
                            "is_stack": is_stack,
                            "is_queue": is_queue,
                            "is_visited": is_visited
                        }
        
        # ===== PHASE 1.5: Resolve variable references =====
        # ✅ FIX 1: Resolve <var:x> placeholders
        changed = True
        while changed:
            changed = False
            for name, state in variable_states.items():
                val = state.get("value")
                if isinstance(val, str) and val.startswith("<var:"):
                    ref_name = val[5:-1]  # extract x from <var:x>
                    if ref_name in variable_states:
                        ref_value = variable_states[ref_name].get("value")
                        if ref_value is not None and not isinstance(ref_value, str):
                            state["value"] = ref_value
                            # Also update data if it's a list
                            if isinstance(ref_value, list):
                                state["data"] = ref_value[:]
                            changed = True
        
        # ===== PHASE 2: Detect graph algorithms =====
        
        detector = GraphDetector(code, variable_states)
        graph_name, graph_data = detector.find_graph()
        algorithm = detector.detect_algorithm()
        
        # ===== PHASE 3: Generate appropriate visualization =====
        
        if algorithm in ['bfs', 'dfs'] and graph_data:
            
            start_node = None
            
            for name in ['start', 'source', 'root', 'begin']:
                if name in variable_states:
                    start_val = variable_states[name].get('value')
                    if start_val in graph_data:
                        start_node = start_val
                        break
            
            if start_node is None:
                start_node = list(graph_data.keys())[0] if graph_data else None
            
            if start_node is not None:
                traversal_steps = simulate_graph_traversal(graph_data, start_node, algorithm)
                
                for i, state in enumerate(traversal_steps):
                    steps.append({
                        "step": i,
                        "line": 1,
                        "code": f"{'BFS' if algorithm == 'bfs' else 'DFS'} Traversal - Step {i + 1}/{len(traversal_steps)}",
                        "description": f"{'Breadth-First Search' if algorithm == 'bfs' else 'Depth-First Search'} algorithm in progress",
                        "visualization": {
                            "type": "graph_with_ds",
                            "graph": state["graph"],
                            "data_structure": state["data_structure"]
                        }
                    })
                
                return steps
        
        if graph_data and algorithm == 'generic':
            nodes = list(graph_data.keys())
            positions = calculate_graph_positions(nodes, graph_data)
            
            steps.append({
                "step": 0,
                "line": 1,
                "code": f"graph = {graph_name}",
                "description": f"Graph structure with {len(nodes)} nodes",
                "visualization": {
                    "type": "graph",
                    "name": graph_name or "graph",
                    "nodes": nodes,
                    "edges": graph_data,
                    "formatted": format_dict_for_display(graph_data),
                    "positions": positions
                }
            })
            
            return steps

        # ===== PHASE 3.5: Detect and simulate sorting algorithms =====
        def detect_and_simulate_sorting():
            """Detect bubble/insertion sort and simulate step by step"""
            code_lower = code.lower()
            
            # Find array variable (first list assignment)
            arr_var = None
            arr_data = None
            for name, state in variable_states.items():
                if state.get('type') == 'list' and isinstance(state.get('data'), list):
                    if all(isinstance(x, (int, float)) for x in state['data']):
                        arr_var = name
                        arr_data = state['data'][:]
                        break
            
            if not arr_var or not arr_data:
                return False

            # Detect bubble sort: nested for loops + tuple swap arr[j], arr[j+1]
            has_tuple_swap = any(
                isinstance(node, ast.Assign) and
                isinstance(node.targets[0], ast.Tuple) and
                any(isinstance(e, ast.Subscript) for e in node.targets[0].elts)
                for node in ast.walk(tree)
                if isinstance(node, ast.Assign) and node.targets
            )

            # Detect insertion sort: while loop + key variable pattern
            has_key_pattern = 'key' in code_lower and 'while' in code_lower

            if has_tuple_swap:
                # Simulate bubble sort
                arr = arr_data[:]
                n = len(arr)
                sort_steps = []
                # Initial state
                sort_steps.append({
                    "step": 0, "line": 1,
                    "code": f"{arr_var} = {arr_data}",
                    "description": f"Initial array '{arr_var}': {arr_data}",
                    "visualization": {
                        "type": "array", "name": arr_var,
                        "data": arr[:], "capacity": n,
                        "highlight": [], "operation": None
                    }
                })
                step_i = 1
                for i in range(n):
                    for j in range(0, n - i - 1):
                        if arr[j] > arr[j + 1]:
                            arr[j], arr[j + 1] = arr[j + 1], arr[j]
                            sort_steps.append({
                                "step": step_i, "line": 1,
                                "code": f"{arr_var}[{j}], {arr_var}[{j+1}] = {arr_var}[{j+1}], {arr_var}[{j}]",
                                "description": f"Swap {arr[j+1]} and {arr[j]} at indices {j} ↔ {j+1}",
                                "visualization": {
                                    "type": "array", "name": arr_var,
                                    "data": arr[:], "capacity": n,
                                    "highlight": [j, j + 1], "operation": "swap"
                                }
                            })
                            step_i += 1
                        else:
                            sort_steps.append({
                                "step": step_i, "line": 1,
                                "code": f"if {arr_var}[{j}] > {arr_var}[{j+1}]",
                                "description": f"Compare {arr[j]} and {arr[j+1]} at indices {j},{j+1} — no swap needed",
                                "visualization": {
                                    "type": "array", "name": arr_var,
                                    "data": arr[:], "capacity": n,
                                    "highlight": [j, j + 1], "operation": "compare"
                                }
                            })
                            step_i += 1
                # Final sorted state
                sort_steps.append({
                    "step": step_i, "line": 1,
                    "code": f"# Sorted!",
                    "description": f"Array '{arr_var}' is now sorted: {arr}",
                    "visualization": {
                        "type": "array", "name": arr_var,
                        "data": arr[:], "capacity": n,
                        "highlight": list(range(n)), "operation": "sorted"
                    }
                })
                steps.extend(sort_steps)
                return True

            elif has_key_pattern:
                # Simulate insertion sort
                arr = arr_data[:]
                n = len(arr)
                sort_steps = []
                sort_steps.append({
                    "step": 0, "line": 1,
                    "code": f"{arr_var} = {arr_data}",
                    "description": f"Initial array '{arr_var}': {arr_data}",
                    "visualization": {
                        "type": "array", "name": arr_var,
                        "data": arr[:], "capacity": n,
                        "highlight": [], "operation": None
                    }
                })
                step_i = 1
                for i in range(1, n):
                    key = arr[i]
                    sort_steps.append({
                        "step": step_i, "line": 1,
                        "code": f"key = {arr_var}[{i}]  # key = {key}",
                        "description": f"Pick key = {key} at index {i}",
                        "visualization": {
                            "type": "array", "name": arr_var,
                            "data": arr[:], "capacity": n,
                            "highlight": [i], "operation": "pick_key"
                        }
                    })
                    step_i += 1
                    j = i - 1
                    while j >= 0 and arr[j] > key:
                        arr[j + 1] = arr[j]
                        sort_steps.append({
                            "step": step_i, "line": 1,
                            "code": f"{arr_var}[{j+1}] = {arr_var}[{j}]  # shift {arr[j+1]}",
                            "description": f"Shift {arr[j+1]} right from index {j} to {j+1}",
                            "visualization": {
                                "type": "array", "name": arr_var,
                                "data": arr[:], "capacity": n,
                                "highlight": [j, j + 1], "operation": "shift"
                            }
                        })
                        step_i += 1
                        j -= 1
                    arr[j + 1] = key
                    sort_steps.append({
                        "step": step_i, "line": 1,
                        "code": f"{arr_var}[{j+1}] = {key}  # insert key",
                        "description": f"Insert key {key} at index {j+1}",
                        "visualization": {
                            "type": "array", "name": arr_var,
                            "data": arr[:], "capacity": n,
                            "highlight": [j + 1], "operation": "insert"
                        }
                    })
                    step_i += 1
                sort_steps.append({
                    "step": step_i, "line": 1,
                    "code": "# Sorted!",
                    "description": f"Array '{arr_var}' is now sorted: {arr}",
                    "visualization": {
                        "type": "array", "name": arr_var,
                        "data": arr[:], "capacity": n,
                        "highlight": list(range(n)), "operation": "sorted"
                    }
                })
                steps.extend(sort_steps)
                return True

            return False

        if detect_and_simulate_sorting():
            return steps

        # ===== PHASE 4: Regular code analysis (arrays, stacks, queues, variables) =====
        
        def process_statement(node):
            """Process a single statement node"""
            nonlocal step_num
            
            # ===== Intercept var = stack.pop() BEFORE variable assignment =====
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        
                        # Check if RHS is a .pop() call on a known list
                        if isinstance(node.value, ast.Call):
                            call = node.value
                            if isinstance(call.func, ast.Attribute) and call.func.attr == 'pop':
                                if isinstance(call.func.value, ast.Name):
                                    obj_name = call.func.value.id
                                    if obj_name in variable_states and variable_states[obj_name]["type"] == "list":
                                        current_data = variable_states[obj_name].get("data", [])[:]
                                        is_stack = variable_states[obj_name].get("is_stack", False)
                                        is_queue = variable_states[obj_name].get("is_queue", False)
                                        is_dequeue = call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value == 0
                                        
                                        if current_data:
                                            if is_dequeue:
                                                popped_value = current_data.pop(0)
                                            else:
                                                popped_value = current_data.pop()
                                            
                                            line_code = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                                            
                                            steps.append({
                                                "step": step_num,
                                                "line": node.lineno,
                                                "code": line_code,
                                                "description": f"{'Pop' if is_stack else 'Dequeue' if is_queue else 'Pop'} {popped_value} from {obj_name} → stored in {var_name}",
                                                "visualization": {
                                                    "type": "stack" if is_stack else "queue" if is_queue else "array",
                                                    "name": obj_name,
                                                    "data": current_data[:],
                                                    "capacity": max(len(current_data), 1),
                                                    "highlight": [],
                                                    "operation": "pop",
                                                    "removed_value": popped_value
                                                }
                                            })
                                            
                                            variable_states[obj_name]["data"] = current_data
                                            variable_states[var_name] = {
                                                "type": "int" if isinstance(popped_value, (int, float)) else "any",
                                                "value": popped_value,
                                                "data": None,
                                                "is_stack": False,
                                                "is_queue": False,
                                                "is_visited": False
                                            }
                                            step_num += 1
                                            return  # Handled, skip normal variable assignment
            
            # ===== Variable assignments =====
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    # ✅ FIX 2: Handle tuple swap: arr[j], arr[j+1] = arr[j+1], arr[j]
                    if isinstance(target, ast.Tuple):
                        # Find the array being swapped
                        for elt in target.elts:
                            if isinstance(elt, ast.Subscript) and isinstance(elt.value, ast.Name):
                                arr_name = elt.value.id
                                if arr_name in variable_states:
                                    # Check if this is a swap operation
                                    if isinstance(node.value, ast.Tuple) and len(node.value.elts) == len(target.elts):
                                        # It's a swap! Update the array data
                                        current_data = variable_states[arr_name].get("data", [])
                                        if current_data:
                                            # Simulate the swap by evaluating indices
                                            indices = []
                                            for t in target.elts:
                                                if isinstance(t, ast.Subscript):
                                                    idx = safe_eval_value(t.slice, variable_states)
                                                    if isinstance(idx, int):
                                                        indices.append(idx)
                                            
                                            # Swap the values in our simulation
                                            if len(indices) == 2:
                                                i, j = indices
                                                if 0 <= i < len(current_data) and 0 <= j < len(current_data):
                                                    current_data[i], current_data[j] = current_data[j], current_data[i]
                                                    variable_states[arr_name]["data"] = current_data
                                                    
                                                    line_code = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                                                    
                                                    steps.append({
                                                        "step": step_num,
                                                        "line": node.lineno,
                                                        "code": line_code,
                                                        "description": f"Swap elements at indices {i} and {j} in '{arr_name}'",
                                                        "visualization": {
                                                            "type": "array",
                                                            "name": arr_name,
                                                            "data": current_data[:],
                                                            "capacity": len(current_data),
                                                            "highlight": [i, j],
                                                            "operation": "swap"
                                                        }
                                                    })
                                                    step_num += 1
                                                    return
                    
                    # Handle regular variable assignments (not tuple targets)
                    elif isinstance(target, ast.Name):
                        var_name = target.id
                        
                        # ✅ FIX 2: Handle n = len(arr)
                        if isinstance(node.value, ast.Call):
                            call = node.value
                            if isinstance(call.func, ast.Name) and call.func.id == 'len':
                                if call.args and isinstance(call.args[0], ast.Name):
                                    arr_name = call.args[0].id
                                    if arr_name in variable_states:
                                        arr_data = variable_states[arr_name].get("data", [])
                                        actual_len = len(arr_data) if arr_data else 0
                                        variable_states[var_name] = {
                                            "type": "int",
                                            "value": actual_len,
                                            "data": None,
                                            "is_stack": False,
                                            "is_queue": False,
                                            "is_visited": False
                                        }
                                        # Don't add a visual step for len() - it's not interesting
                                        step_num += 1
                                        return
                        
                        # Regular assignment with value evaluation
                        var_type = detect_type(node.value, variable_states)
                        actual_value = safe_eval_value(node.value, variable_states)
                        
                        line_code = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                        
                        # Dictionary visualization
                        if var_type == "dict" or (isinstance(actual_value, dict) and actual_value):
                            dict_data = actual_value if isinstance(actual_value, dict) else {}
                            
                            steps.append({
                                "step": step_num,
                                "line": node.lineno,
                                "code": line_code,
                                "description": f"Create dictionary '{var_name}' with {len(dict_data)} key(s)",
                                "visualization": {
                                    "type": "dict",
                                    "name": var_name,
                                    "data": dict_data,
                                    "formatted": format_dict_for_display(dict_data)
                                }
                            })
                        
                        # List/Array/Stack/Queue visualization
                        elif var_type == "list" or isinstance(actual_value, list):
                            initial_data = actual_value if isinstance(actual_value, list) else []
                            
                            # Read from stored metadata
                            is_stack = variable_states[var_name].get("is_stack", False)
                            is_queue = variable_states[var_name].get("is_queue", False)
                            is_visited = variable_states[var_name].get("is_visited", False)
                            
                            if is_stack:
                                steps.append({
                                    "step": step_num,
                                    "line": node.lineno,
                                    "code": line_code,
                                    "description": f"Create stack '{var_name}' (LIFO - Last In, First Out) with {len(initial_data)} element(s)",
                                    "visualization": {
                                        "type": "stack",
                                        "name": var_name,
                                        "data": initial_data[:],
                                        "highlight": [len(initial_data) - 1] if initial_data else [],
                                        "operation": None
                                    }
                                })
                            elif is_queue:
                                steps.append({
                                    "step": step_num,
                                    "line": node.lineno,
                                    "code": line_code,
                                    "description": f"Create queue '{var_name}' (FIFO) with {len(initial_data)} element(s)",
                                    "visualization": {
                                        "type": "queue",
                                        "name": var_name,
                                        "data": initial_data[:],
                                        "capacity": max(len(initial_data), 1),
                                        "highlight": list(range(len(initial_data))) if initial_data else []
                                    }
                                })
                            elif is_visited:
                                steps.append({
                                    "step": step_num,
                                    "line": node.lineno,
                                    "code": line_code,
                                    "description": f"Create visited set '{var_name}' with {len(initial_data)} element(s)",
                                    "visualization": {
                                        "type": "visited",
                                        "name": var_name,
                                        "data": initial_data[:],
                                        "capacity": max(len(initial_data), 1),
                                        "highlight": list(range(len(initial_data))) if initial_data else []
                                    }
                                })
                            else:
                                steps.append({
                                    "step": step_num,
                                    "line": node.lineno,
                                    "code": line_code,
                                    "description": f"Create array '{var_name}' with {len(initial_data)} element(s)",
                                    "visualization": {
                                        "type": "array",
                                        "name": var_name,
                                        "data": initial_data[:],
                                        "capacity": max(len(initial_data), 1),
                                        "highlight": list(range(len(initial_data))) if initial_data else []
                                    }
                                })
                        
                        # Simple variable
                        else:
                            steps.append({
                                "step": step_num,
                                "line": node.lineno,
                                "code": line_code,
                                "description": f"Set {var_name} = {actual_value}",
                                "visualization": {
                                    "type": "variable",
                                    "name": var_name,
                                    "value": str(actual_value),
                                    "var_type": var_type
                                }
                            })
                        
                        step_num += 1
            
            # Standalone list operations (append, pop, etc.) - NOT assignments
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                
                if isinstance(call.func, ast.Attribute):
                    method_name = call.func.attr
                    
                    # Append operation (PUSH for stacks, ENQUEUE for queues)
                    if method_name == 'append':
                        if isinstance(call.func.value, ast.Name):
                            obj_name = call.func.value.id
                            
                            if obj_name in variable_states and variable_states[obj_name]["type"] == "list":
                                if call.args:
                                    new_value = safe_eval_value(call.args[0], variable_states)
                                    
                                    # Clone the array
                                    current_data = variable_states[obj_name].get("data", [])
                                    current_data = current_data[:] if current_data else []
                                    current_data.append(new_value)
                                    
                                    line_code = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                                    
                                    # Read from stored metadata
                                    is_stack = variable_states[obj_name].get("is_stack", False)
                                    is_queue = variable_states[obj_name].get("is_queue", False)
                                    
                                    steps.append({
                                        "step": step_num,
                                        "line": node.lineno,
                                        "code": line_code,
                                        "description": f"{'Push' if is_stack else 'Enqueue' if is_queue else 'Append'} {new_value} to {obj_name}",
                                        "visualization": {
                                            "type": "stack" if is_stack else "queue" if is_queue else "array",
                                            "name": obj_name,
                                            "data": current_data[:],
                                            "capacity": len(current_data),
                                            "highlight": [len(current_data) - 1],
                                            "operation": "push" if is_stack else "enqueue" if is_queue else "push_back"
                                        }
                                    })
                                    
                                    variable_states[obj_name]["data"] = current_data
                                    step_num += 1
                    
                    # Standalone pop operation (not assigned to a variable)
                    elif method_name == 'pop':
                        if isinstance(call.func.value, ast.Name):
                            obj_name = call.func.value.id
                            
                            if obj_name in variable_states and variable_states[obj_name]["type"] == "list":
                                current_data = variable_states[obj_name].get("data", [])
                                
                                if current_data:
                                    # Clone before modifying
                                    current_data = current_data[:]
                                    
                                    # Read from stored metadata
                                    is_stack = variable_states[obj_name].get("is_stack", False)
                                    
                                    # Check if pop(0) (FIFO) or pop() (LIFO)
                                    is_dequeue = False
                                    if call.args and isinstance(call.args[0], ast.Constant):
                                        if call.args[0].value == 0:
                                            is_dequeue = True
                                            popped_value = current_data[0]
                                            current_data = current_data[1:]
                                        else:
                                            popped_value = current_data[-1]
                                            current_data = current_data[:-1]
                                    else:
                                        # Default pop() - LIFO
                                        popped_value = current_data[-1]
                                        current_data = current_data[:-1]
                                    
                                    line_code = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                                    
                                    steps.append({
                                        "step": step_num,
                                        "line": node.lineno,
                                        "code": line_code,
                                        "description": f"{'Pop' if is_stack else 'Dequeue' if is_dequeue else 'Remove'} {popped_value} from {obj_name}",
                                        "visualization": {
                                            "type": "stack" if is_stack else "queue" if is_dequeue else "array",
                                            "name": obj_name,
                                            "data": current_data[:],
                                            "capacity": len(current_data) if current_data else 1,
                                            "highlight": [],
                                            "operation": "pop",
                                            "removed_value": popped_value
                                        }
                                    })
                                    
                                    variable_states[obj_name]["data"] = current_data
                                    step_num += 1
            
            # Recursively process nested statements (for loops, if statements, etc.)
            elif isinstance(node, (ast.For, ast.While, ast.If)):
                for stmt in node.body:
                    process_statement(stmt)
                for stmt in getattr(node, 'orelse', []):
                    process_statement(stmt)
        
        # ===== Process all statements in order =====
        for statement in tree.body:
            process_statement(statement)
        
        if not steps:
            steps.append({
                "step": 0,
                "line": 1,
                "code": "# No visualizable operations found",
                "description": "Try code with: BFS/DFS graph traversal, stacks, arrays, queues, or data structures",
                "visualization": {
                    "type": "none",
                    "message": "💡 Example:\nstack = []\nstack.append(10)\nstack.append(20)\nstack.pop()\n\nOr try BFS/DFS!"
                }
            })
    
    except SyntaxError as e:
        steps = [{
            "step": 0,
            "line": e.lineno or 0,
            "code": "",
            "description": f"Syntax Error on line {e.lineno}: {str(e)}",
            "visualization": {
                "type": "error",
                "message": f"❌ Fix the syntax error: {str(e)}"
            }
        }]
    
    except Exception as e:
        print(f"❌ Error generating steps: {e}")
        import traceback
        traceback.print_exc()
        
        steps = [{
            "step": 0,
            "line": 0,
            "code": "",
            "description": f"Analysis Error: {str(e)}",
            "visualization": {
                "type": "error",
                "message": f"⚠️ Could not analyze code: {str(e)}"
            }
        }]
    
    return steps


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test with stack code including var = stack.pop()
    test_stack_code = """
stack = []
stack.append(10)
stack.append(20)
stack.append(30)
top = stack.pop()
second = stack.pop()
"""
    
    print("Testing Stack visualization (LIFO)...")
    steps = generate_execution_steps(test_stack_code, "python")
    print(f"Generated {len(steps)} steps\n")
    
    for i, step in enumerate(steps):
        print(f"Step {i}:")
        print(f"  Line: {step['line']}")
        print(f"  Code: {step['code']}")
        print(f"  Description: {step['description']}")
        viz = step['visualization']
        print(f"  Type: {viz['type']}")
        if 'data' in viz:
            print(f"  Data: {viz['data']}")
        if 'operation' in viz:
            print(f"  Operation: {viz.get('operation')}")
        if 'removed_value' in viz:
            print(f"  Removed: {viz.get('removed_value')}")
        print()
    
    print("="*60)
    
    # Test with bubble sort
    test_bubble_code = """
arr = [5, 2, 8, 1, 9]
n = len(arr)
for i in range(n):
    for j in range(0, n-i-1):
        if arr[j] > arr[j+1]:
            arr[j], arr[j+1] = arr[j+1], arr[j]
"""
    
    print("\nTesting Bubble Sort visualization...")
    steps = generate_execution_steps(test_bubble_code, "python")
    print(f"Generated {len(steps)} steps")
    
    for i, step in enumerate(steps[:5]):
        print(f"\nStep {i}:")
        print(f"  Description: {step['description']}")
        print(f"  Type: {step['visualization']['type']}")
        if step['visualization']['type'] == 'array':
            print(f"  Data: {step['visualization'].get('data')}")
    
    print("="*60)
    
    # Test with BFS graph
    test_bfs_code = """
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}
start = 'A'
queue = [start]
visited = []

while queue:
    node = queue.pop(0)
    if node not in visited:
        visited.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append(neighbor)
"""
    
    print("\n\nTesting BFS graph visualization...")
    steps = generate_execution_steps(test_bfs_code, "python")
    print(f"Generated {len(steps)} steps")
    
    if steps and steps[0]['visualization']['type'] == 'graph_with_ds':
        print("✅ BFS correctly detected and simulated!")
        print(f"  Total steps: {len(steps)}")
    else:
        print("⚠️ BFS fell back to regular processing")