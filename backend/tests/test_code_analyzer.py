"""Simple tests for code_analyzer.py"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code_analyzer import generate_execution_steps


def test_simple_variable():
    """Test parsing a simple variable"""
    code = "x = 5"
    steps = generate_execution_steps(code, "python")
    
    assert len(steps) > 0
    assert steps[0]['visualization']['type'] == 'variable'


def test_array_creation():
    """Test creating an array"""
    code = "arr = [1, 2, 3]"
    steps = generate_execution_steps(code, "python")
    
    assert len(steps) > 0
    assert steps[0]['visualization']['type'] == 'array'


def test_stack_operations():
    """Test stack operations"""
    code = "stack = []\nstack.append(10)"
    steps = generate_execution_steps(code, "python")
    
    assert len(steps) >= 2


def test_empty_code():
    """Test empty code handling"""
    code = ""
    steps = generate_execution_steps(code, "python")
    
    assert len(steps) > 0


def test_syntax_error():
    """Test syntax error handling"""
    code = "if x = 5:"
    steps = generate_execution_steps(code, "python")
    
    assert len(steps) > 0
    assert steps[0]['visualization']['type'] == 'error'