"""
Enhanced Code Analyzer - Supports animated BFS/DFS graph traversals
"""
import ast
from typing import List, Dict, Any

def safe_eval_value(node):
    """Safely evaluate expressions to get actual values"""
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
                result[k] = v
            return result
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
                return left / right
        elif isinstance(node, ast.UnaryOp):
            operand = safe_eval_value(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    except:
        return ast.unparse(node) if hasattr(ast, 'unparse') else "..."


def detect_type(node) -> str:
    """Detect variable type from AST node"""
    if isinstance(node, ast.List):
        return "list"
    elif isinstance(node, ast.Dict):
        return "dict"
    elif isinstance(node, ast.Set):
        return "set"
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, int):
            return "int"
        elif isinstance(node.value, float):
            return "float"
        elif isinstance(node.value, str):
            return "string"
        elif isinstance(node.value, bool):
            return "bool"
    elif isinstance(node, ast.Call):
        if hasattr(node.func, 'id'):
            func_name = node.func.id
            if func_name in ['list', 'dict', 'set', 'tuple']:
                return func_name
    return "unknown"


def format_dict_for_display(d, max_items=5):
    """Format dictionary for visual display"""
    if not isinstance(d, dict):
        return str(d)
    
    items = list(d.items())[:max_items]
    formatted = []
    for k, v in items:
        if isinstance(v, list):
            v_str = f"[{', '.join(map(str, v[:3]))}{'...' if len(v) > 3 else ''}]"
        else:
            v_str = str(v)
        formatted.append(f"{k}: {v_str}")
    
    if len(d) > max_items:
        formatted.append("...")
    
    return formatted


def calculate_graph_positions(nodes, edges):
    """Calculate optimal positions for graph nodes in a circle layout"""
    import math
    
    n = len(nodes)
    if n == 0:
        return {}
    
    # Center of the canvas
    center_x, center_y = 400, 250
    radius = min(150, 50 + n * 10)
    
    positions = {}
    for i, node in enumerate(nodes):
        angle = (2 * math.pi * i) / n - (math.pi / 2)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions[node] = {"x": int(x), "y": int(y)}
    
    return positions


def simulate_bfs_dfs(graph_data, start_node, algorithm="bfs"):
    """Simulate BFS/DFS traversal and generate step-by-step states"""
    edges = graph_data
    nodes = list(edges.keys())
    
    if start_node not in nodes:
        start_node = nodes[0] if nodes else None
    
    if not start_node:
        return []
    
    visited = []
    queue_or_stack = [start_node]
    traversal_steps = []
    
    positions = calculate_graph_positions(nodes, edges)
    
    # Initial state
    traversal_steps.append({
        "graph": {
            "name": "graph",
            "nodes": nodes,
            "edges": edges,
            "positions": positions,
            "current_node": None,
            "visited": [],
            "exploring": []
        },
        "data_structure": {
            "type": "queue" if algorithm == "bfs" else "stack",
            "name": "queue" if algorithm == "bfs" else "stack",
            "data": [start_node],
            "highlight": [0],
            "operation": "enqueue" if algorithm == "bfs" else "push"
        }
    })
    
    while queue_or_stack:
        # Dequeue/Pop
        if algorithm == "bfs":
            current = queue_or_stack.pop(0)
        else:
            current = queue_or_stack.pop()
        
        if current not in visited:
            visited.append(current)
            
            # After dequeue, before visiting
            traversal_steps.append({
                "graph": {
                    "name": "graph",
                    "nodes": nodes,
                    "edges": edges,
                    "positions": positions,
                    "current_node": current,
                    "visited": visited[:],
                    "exploring": []
                },
                "data_structure": {
                    "type": "queue" if algorithm == "bfs" else "stack",
                    "name": "queue" if algorithm == "bfs" else "stack",
                    "data": queue_or_stack[:],
                    "removed_value": current,
                    "operation": "dequeue" if algorithm == "bfs" else "pop"
                }
            })
            
            # Explore neighbors
            neighbors = edges.get(current, [])
            for neighbor in neighbors:
                if neighbor not in visited and neighbor not in queue_or_stack:
                    queue_or_stack.append(neighbor)
                    
                    # Show neighbor being added
                    traversal_steps.append({
                        "graph": {
                            "name": "graph",
                            "nodes": nodes,
                            "edges": edges,
                            "positions": positions,
                            "current_node": current,
                            "visited": visited[:],
                            "exploring": [neighbor]
                        },
                        "data_structure": {
                            "type": "queue" if algorithm == "bfs" else "stack",
                            "name": "queue" if algorithm == "bfs" else "stack",
                            "data": queue_or_stack[:],
                            "highlight": [len(queue_or_stack) - 1],
                            "operation": "enqueue" if algorithm == "bfs" else "push"
                        }
                    })
    
    # Final state
    traversal_steps.append({
        "graph": {
            "name": "graph",
            "nodes": nodes,
            "edges": edges,
            "positions": positions,
            "current_node": None,
            "visited": visited,
            "exploring": []
        },
        "data_structure": {
            "type": "queue" if algorithm == "bfs" else "stack",
            "name": "queue" if algorithm == "bfs" else "stack",
            "data": [],
            "operation": None
        }
    })
    
    return traversal_steps


def detect_bfs_dfs_pattern(code: str, variable_states: dict):
    """Detect if code contains BFS or DFS pattern"""
    code_lower = code.lower()
    
    has_graph = any('graph' in name or isinstance(state.get('data'), dict) 
                   for name, state in variable_states.items() 
                   if state.get('type') == 'dict')
    
    has_queue = any('queue' in name or 'q' == name 
                   for name in variable_states.keys())
    
    has_stack = any('stack' in name or 's' == name 
                   for name in variable_states.keys())
    
    has_visited = any('visited' in name 
                     for name in variable_states.keys())
    
    has_pop_0 = 'pop(0)' in code or '.popleft()' in code
    has_append = '.append(' in code
    
    # BFS pattern: graph + queue + visited + pop(0)
    if has_graph and has_queue and has_visited and has_pop_0:
        return "bfs"
    
    # DFS pattern: graph + stack + visited + pop()
    if has_graph and (has_stack or has_queue) and has_visited and has_append:
        if not has_pop_0:
            return "dfs"
    
    return None


def generate_execution_steps(code: str, language: str = "python") -> List[Dict[str, Any]]:
    """Generate step-by-step execution visualization with animated BFS/DFS"""
    
    steps = []
    
    if language != "python":
        return [{
            "step": 0,
            "line": 1,
            "code": f"# {language} visualization coming soon",
            "description": f"Only Python is currently supported for visualization",
            "visualization": {
                "type": "none",
                "message": f"{language} visualization not yet implemented"
            }
        }]
    
    try:
        lines = code.split('\n')
        tree = ast.parse(code)
        
        step_num = 0
        variable_states = {}
        graph_data = None
        start_node = None
        algorithm = None
        
        # First pass: collect all variable assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        var_type = detect_type(node.value)
                        actual_value = safe_eval_value(node.value)
                        
                        variable_states[var_name] = {
                            "type": var_type,
                            "value": actual_value,
                            "data": actual_value if isinstance(actual_value, (list, dict)) else None
                        }
                        
                        # Detect graph
                        if var_type == "dict" and isinstance(actual_value, dict):
                            if actual_value and isinstance(list(actual_value.values())[0], list):
                                graph_data = actual_value
        
        # Detect BFS/DFS pattern
        algorithm = detect_bfs_dfs_pattern(code, variable_states)
        
        # If BFS/DFS detected, generate animated traversal
        if algorithm and graph_data:
            start_node = list(graph_data.keys())[0]
            
            # Check if there's an explicit start node in code
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id in ['start', 'source', 'root']:
                            start_val = safe_eval_value(node.value)
                            if start_val in graph_data:
                                start_node = start_val
            
            traversal_steps = simulate_bfs_dfs(graph_data, start_node, algorithm)
            
            for i, state in enumerate(traversal_steps):
                steps.append({
                    "step": i,
                    "line": 1,
                    "code": f"{'BFS' if algorithm == 'bfs' else 'DFS'} Traversal - Step {i + 1}",
                    "description": f"{'Breadth-First' if algorithm == 'bfs' else 'Depth-First'} Search traversal in progress",
                    "visualization": {
                        "type": "graph_with_ds",
                        "graph": state["graph"],
                        "data_structure": state["data_structure"]
                    }
                })
            
            return steps
        
        # Regular analysis (existing code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        var_type = detect_type(node.value)
                        actual_value = safe_eval_value(node.value)
                        
                        if var_type == "dict":
                            dict_data = actual_value if isinstance(actual_value, dict) else {}
                            is_graph = False
                            if dict_data and isinstance(list(dict_data.values())[0], list):
                                is_graph = True
                            
                            steps.append({
                                "step": step_num,
                                "line": node.lineno,
                                "code": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                                "description": f"Create {'graph' if is_graph else 'dictionary'} '{var_name}' with {len(dict_data)} {'nodes' if is_graph else 'keys'}",
                                "visualization": {
                                    "type": "graph" if is_graph else "dict",
                                    "name": var_name,
                                    "data": dict_data,
                                    "nodes": list(dict_data.keys()) if is_graph else None,
                                    "edges": dict_data if is_graph else None,
                                    "formatted": format_dict_for_display(dict_data)
                                }
                            })
                            
                            variable_states[var_name] = {
                                "type": "dict",
                                "data": dict_data,
                                "is_graph": is_graph
                            }
                        
                        elif var_type == "list":
                            initial_data = []
                            if isinstance(node.value, ast.List):
                                initial_data = [safe_eval_value(elt) for elt in node.value.elts]
                            
                            is_queue = 'queue' in var_name.lower() or 'q' == var_name.lower()
                            is_visited = 'visited' in var_name.lower()
                            
                            steps.append({
                                "step": step_num,
                                "line": node.lineno,
                                "code": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                                "description": f"Create {var_type} '{var_name}' {'(queue)' if is_queue else '(visited tracker)' if is_visited else ''} with {len(initial_data)} element(s)",
                                "visualization": {
                                    "type": "queue" if is_queue else "visited" if is_visited else "array",
                                    "name": var_name,
                                    "data": initial_data,
                                    "capacity": max(len(initial_data), 1),
                                    "highlight": list(range(len(initial_data))) if initial_data else []
                                }
                            })
                            
                            variable_states[var_name] = {
                                "type": "list",
                                "data": initial_data,
                                "is_queue": is_queue,
                                "is_visited": is_visited
                            }
                        
                        else:
                            steps.append({
                                "step": step_num,
                                "line": node.lineno,
                                "code": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                                "description": f"Assign {actual_value} to variable '{var_name}'",
                                "visualization": {
                                    "type": "variable",
                                    "name": var_name,
                                    "value": str(actual_value),
                                    "var_type": var_type
                                }
                            })
                            
                            variable_states[var_name] = {
                                "type": var_type,
                                "value": actual_value
                            }
                        
                        step_num += 1
            
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                
                if isinstance(call.func, ast.Attribute):
                    method_name = call.func.attr
                    
                    if method_name in ['append']:
                        if isinstance(call.func.value, ast.Name):
                            obj_name = call.func.value.id
                            
                            if obj_name in variable_states and variable_states[obj_name]["type"] == "list":
                                if call.args:
                                    new_value = safe_eval_value(call.args[0])
                                    current_data = variable_states[obj_name].get("data", [])
                                    current_data.append(new_value)
                                    
                                    is_queue = variable_states[obj_name].get("is_queue", False)
                                    is_visited = variable_states[obj_name].get("is_visited", False)
                                    
                                    description = f"Append {new_value} to {obj_name}"
                                    if is_queue:
                                        description = f"Enqueue {new_value} to queue"
                                    elif is_visited:
                                        description = f"Mark {new_value} as visited"
                                    
                                    steps.append({
                                        "step": step_num,
                                        "line": node.lineno,
                                        "code": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                                        "description": description,
                                        "visualization": {
                                            "type": "queue" if is_queue else "visited" if is_visited else "array",
                                            "name": obj_name,
                                            "data": current_data.copy(),
                                            "capacity": len(current_data),
                                            "highlight": [len(current_data) - 1],
                                            "operation": "enqueue" if is_queue else "mark_visited" if is_visited else "push_back"
                                        }
                                    })
                                    
                                    variable_states[obj_name]["data"] = current_data
                                    step_num += 1
                    
                    elif method_name in ['pop']:
                        if isinstance(call.func.value, ast.Name):
                            obj_name = call.func.value.id
                            
                            if obj_name in variable_states and variable_states[obj_name]["type"] == "list":
                                current_data = variable_states[obj_name].get("data", [])
                                
                                if current_data:
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
                                        popped_value = current_data[-1]
                                        current_data = current_data[:-1]
                                    
                                    is_queue = variable_states[obj_name].get("is_queue", False)
                                    
                                    description = f"Remove {popped_value} from {obj_name}"
                                    if is_queue or is_dequeue:
                                        description = f"Dequeue {popped_value} (process node)"
                                    
                                    steps.append({
                                        "step": step_num,
                                        "line": node.lineno,
                                        "code": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                                        "description": description,
                                        "visualization": {
                                            "type": "queue" if is_queue else "array",
                                            "name": obj_name,
                                            "data": current_data.copy(),
                                            "capacity": len(current_data) if current_data else 1,
                                            "highlight": [],
                                            "operation": "dequeue" if (is_queue or is_dequeue) else "pop",
                                            "removed_value": popped_value
                                        }
                                    })
                                    
                                    variable_states[obj_name]["data"] = current_data
                                    step_num += 1
        
        if not steps:
            steps.append({
                "step": 0,
                "line": 1,
                "code": lines[0] if lines else "",
                "description": "No visualizable operations detected. Try BFS/DFS algorithms!",
                "visualization": {
                    "type": "none",
                    "message": "Try: graph = {'A': ['B', 'C']}, queue = ['A'], visited = []"
                }
            })
    
    except SyntaxError as e:
        steps = [{
            "step": 0,
            "line": e.lineno or 0,
            "code": "",
            "description": f"Syntax Error: {str(e)}",
            "visualization": {
                "type": "error",
                "message": f"Fix syntax error: {str(e)}"
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
            "description": f"Error: {str(e)}",
            "visualization": {
                "type": "error",
                "message": f"Error analyzing code: {str(e)}"
            }
        }]
    
    return steps