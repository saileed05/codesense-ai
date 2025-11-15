"""
Enhanced Code Analyzer v2.2 - FIXED DUPLICATE CODE BUG
Supports ANY graph algorithm visualization: BFS, DFS, Dijkstra, and generic graphs
✅ CRITICAL FIX: Removed duplicate code that was overwriting stack metadata
"""
import ast
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import deque


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def safe_eval_value(node):
    """Safely evaluate AST expressions to get actual values"""
    try:
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.List):
            return [safe_eval_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Dict):
            result = {}
            for key, value in zip(node.keys, node.values):
                k = safe_eval_value(key)
                v = safe_eval_value(value)
                if k is not None:
                    result[k] = v
            return result
        elif isinstance(node, ast.Set):
            return {safe_eval_value(elt) for elt in node.elts}
        elif isinstance(node, ast.Tuple):
            return tuple(safe_eval_value(elt) for elt in node.elts)
        elif isinstance(node, ast.BinOp):
            left = safe_eval_value(node.left)
            right = safe_eval_value(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right if right != 0 else float('inf')
        elif isinstance(node, ast.UnaryOp):
            operand = safe_eval_value(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.UAdd):
                return +operand
        elif isinstance(node, ast.Name):
            return f"<var:{node.id}>"
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    except:
        try:
            return ast.unparse(node) if hasattr(ast, 'unparse') else "..."
        except:
            return "..."


def detect_type(node) -> str:
    """Detect variable type from AST node"""
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
        
        if '.pop(0)' in code or '.popleft()' in code:
            has_list_structure = any(
                state.get('type') in ['list', 'deque'] 
                for state in self.states.values()
            )
            if has_list_structure:
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
    
    if not start_node:
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
    ✅ FIXED VERSION: No duplicate code processing
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
                            "is_stack": is_stack,    # ✅ PERSIST THIS
                            "is_queue": is_queue,    # ✅ PERSIST THIS
                            "is_visited": is_visited # ✅ PERSIST THIS
                        }
        
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
            
            if not start_node:
                start_node = list(graph_data.keys())[0] if graph_data else None
            
            if start_node:
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
        
        # ===== PHASE 4: Regular code analysis (arrays, stacks, queues, variables) =====
        # ✅ CRITICAL FIX: Process statements IN ORDER using a single pass
        
        def process_statement(node):
            """Process a single statement node"""
            nonlocal step_num
            
            # Variable assignments
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        var_type = detect_type(node.value)
                        actual_value = safe_eval_value(node.value)
                        
                        line_code = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                        
                        # Dictionary visualization
                        if var_type == "dict":
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
                        elif var_type == "list":
                            initial_data = []
                            if isinstance(node.value, ast.List):
                                initial_data = [safe_eval_value(elt) for elt in node.value.elts]
                            
                            # ✅ Read from stored metadata
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
            
            # List operations (append, pop, etc.)
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
                                    new_value = safe_eval_value(call.args[0])
                                    
                                    # ✅ Clone the array
                                    current_data = variable_states[obj_name].get("data", [])
                                    current_data = current_data[:] if current_data else []
                                    current_data.append(new_value)
                                    
                                    line_code = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                                    
                                    # ✅ CRITICAL FIX: Read from stored metadata
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
                    
                    # Pop operation (POP for stacks, DEQUEUE for queues)
                    elif method_name == 'pop':
                        if isinstance(call.func.value, ast.Name):
                            obj_name = call.func.value.id
                            
                            if obj_name in variable_states and variable_states[obj_name]["type"] == "list":
                                current_data = variable_states[obj_name].get("data", [])
                                
                                if current_data:
                                    # ✅ Clone before modifying
                                    current_data = current_data[:]
                                    
                                    # ✅ CRITICAL FIX: Read from stored metadata
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
                                        # ✅ Default pop() - LIFO
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
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, list):
                        for item in child:
                            process_statement(item)
                    else:
                        process_statement(child)
        
        # ✅ CRITICAL FIX: Process all statements in order - NO DUPLICATE CODE AFTER THIS
        for statement in tree.body:
            process_statement(statement)
        
        # ===== END OF PROCESSING - NO MORE CODE SHOULD BE HERE =====
        
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
    # Test with stack code
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
    print("\nExpected behavior:")
    print("  Step 0: Create empty stack []")
    print("  Step 1: Push 10 -> [10]")
    print("  Step 2: Push 20 -> [10, 20]")
    print("  Step 3: Push 30 -> [10, 20, 30]")
    print("  Step 4: Pop 30 -> [10, 20]")
    print("  Step 5: Pop 20 -> [10]")
    print("\n✅ All steps should show type='stack', not 'array'!")
    print("="*60)
    
    # Test with BFS code
    test_bfs_code = """
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}

queue = ['A']
visited = []

while queue:
    node = queue.pop(0)
    if node not in visited:
        visited.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append(neighbor)
"""
    
    print("\n\nTesting BFS visualization...")
    steps = generate_execution_steps(test_bfs_code, "python")
    print(f"Generated {len(steps)} steps")
    
    for i, step in enumerate(steps[:3]):
        print(f"\nStep {i}:")
        print(f"  Description: {step['description']}")
        print(f"  Viz type: {step['visualization']['type']}")