"""
Code Analyzer - Parse and extract structure from code
"""
import ast
import re
from typing import List, Dict, Any

def parse_python_code(code: str) -> Dict[str, Any]:
    """
    Parse Python code and extract structure
    """
    result = {
        "success": True,
        "variables": [],
        "functions": [],
        "loops": [],
        "data_structures": [],
        "execution_flow": []
    }
    
    try:
        tree = ast.parse(code)
        
        # Extract all assignments (variables)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_type = detect_type(node.value)
                        result["variables"].append({
                            "name": target.id,
                            "line": node.lineno,
                            "type": var_type,
                            "initial_value": ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value)
                        })
                        
                        # Track data structure creation
                        if var_type in ["list", "dict", "set", "vector"]:
                            result["data_structures"].append({
                                "name": target.id,
                                "type": var_type,
                                "line": node.lineno
                            })
            
            # Extract functions
            elif isinstance(node, ast.FunctionDef):
                result["functions"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "has_return": any(isinstance(n, ast.Return) for n in ast.walk(node))
                })
            
            # Extract loops
            elif isinstance(node, (ast.For, ast.While)):
                loop_type = "for" if isinstance(node, ast.For) else "while"
                result["loops"].append({
                    "type": loop_type,
                    "line": node.lineno,
                    "variable": node.target.id if isinstance(node, ast.For) and isinstance(node.target, ast.Name) else None
                })
        
    except SyntaxError as e:
        result["success"] = False
        result["error"] = f"Syntax error: {str(e)}"
    
    return result


def detect_type(node) -> str:
    """
    Detect variable type from AST node
    """
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


def generate_execution_steps(code: str, language: str = "python") -> List[Dict[str, Any]]:
    """
    Generate step-by-step execution visualization data
    """
    steps = []
    
    if language != "python":
        return steps
    
    try:
        lines = code.split('\n')
        tree = ast.parse(code)
        
        step_num = 0
        variable_states = {}  # Track variable values over time
        
        # Process each line/node
        for node in ast.walk(tree):
            # Variable assignment
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        var_type = detect_type(node.value)
                        
                        # Determine visualization type
                        if var_type == "list":
                            viz_type = "array"
                            # Try to extract initial values
                            initial_data = []
                            if isinstance(node.value, ast.List):
                                initial_data = [ast.unparse(elt) if hasattr(ast, 'unparse') else str(elt) for elt in node.value.elts]
                            
                            steps.append({
                                "step": step_num,
                                "line": node.lineno,
                                "code": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                                "description": f"Create {var_type} '{var_name}'",
                                "visualization": {
                                    "type": "array",
                                    "name": var_name,
                                    "data": initial_data,
                                    "capacity": len(initial_data),
                                    "highlight": list(range(len(initial_data)))
                                }
                            })
                            
                            variable_states[var_name] = {
                                "type": var_type,
                                "data": initial_data
                            }
                        
                        else:
                            # Simple variable
                            value = ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value)
                            steps.append({
                                "step": step_num,
                                "line": node.lineno,
                                "code": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                                "description": f"Set {var_name} = {value}",
                                "visualization": {
                                    "type": "variable",
                                    "name": var_name,
                                    "value": value,
                                    "var_type": var_type
                                }
                            })
                            
                            variable_states[var_name] = {
                                "type": var_type,
                                "value": value
                            }
                        
                        step_num += 1
            
            # Method calls (like append, push_back)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Attribute):
                    method_name = call.func.attr
                    
                    if method_name in ['append', 'push_back', 'insert']:
                        # Get the object name
                        if isinstance(call.func.value, ast.Name):
                            obj_name = call.func.value.id
                            
                            if obj_name in variable_states and variable_states[obj_name]["type"] == "list":
                                # Get the value being added
                                if call.args:
                                    new_value = ast.unparse(call.args[0]) if hasattr(ast, 'unparse') else str(call.args[0])
                                    
                                    # Update state
                                    current_data = variable_states[obj_name].get("data", [])
                                    current_data.append(new_value)
                                    
                                    steps.append({
                                        "step": step_num,
                                        "line": node.lineno,
                                        "code": lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                                        "description": f"Append {new_value} to {obj_name}",
                                        "visualization": {
                                            "type": "array",
                                            "name": obj_name,
                                            "data": current_data.copy(),
                                            "capacity": max(len(current_data), 1),
                                            "highlight": [len(current_data) - 1],
                                            "operation": "push_back"
                                        }
                                    })
                                    
                                    variable_states[obj_name]["data"] = current_data
                                    step_num += 1
        
        # If no steps generated, create a placeholder
        if not steps:
            steps.append({
                "step": 0,
                "line": 1,
                "code": lines[0] if lines else "",
                "description": "Code execution started",
                "visualization": {
                    "type": "none",
                    "message": "No visualizable operations detected"
                }
            })
    
    except Exception as e:
        print(f"Error generating steps: {e}")
        steps = [{
            "step": 0,
            "line": 0,
            "code": "",
            "description": f"Error: {str(e)}",
            "visualization": {"type": "error", "message": str(e)}
        }]
    
    return steps