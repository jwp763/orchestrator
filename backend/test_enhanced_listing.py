#!/usr/bin/env python3
"""Test script for enhanced task listing functionality."""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.storage.sql_implementation import SQLStorage
from src.models.task import Task
from src.models.project import Project

def test_enhanced_listing():
    """Test the enhanced task listing functionality."""
    storage = SQLStorage()
    
    print("=== TESTING ENHANCED TASK LISTING ===")
    
    # Test 1: Basic listing with default ordering (newest first)
    print("\n1. Testing default listing (newest first, limit 5):")
    result = storage.list_tasks(skip=0, limit=5)
    print(f"Total tasks: {result['total']}")
    print(f"Returned tasks: {len(result['tasks'])}")
    print(f"Page info: page={result['page']}, has_next={result['has_next']}, has_prev={result['has_prev']}")
    
    if result['tasks']:
        print("First 3 tasks:")
        for i, task in enumerate(result['tasks'][:3]):
            print(f"  {i+1}. '{task.title}' (created: {task.created_at})")
    
    # Test 2: Search functionality
    print("\n2. Testing search functionality (search='test'):")
    search_result = storage.list_tasks(search="test", limit=5)
    print(f"Found {search_result['total']} tasks containing 'test'")
    if search_result['tasks']:
        for task in search_result['tasks'][:3]:
            print(f"  - '{task.title}' in project {task.project_id[:8]}...")
    
    # Test 3: Filtering by status
    print("\n3. Testing status filtering (status='todo'):")
    status_result = storage.list_tasks(status="todo", limit=5)
    print(f"Found {status_result['total']} tasks with status 'todo'")
    
    # Test 4: Sorting by title
    print("\n4. Testing sorting by title (ascending):")
    sort_result = storage.list_tasks(sort_by="title", sort_order="asc", limit=5)
    if sort_result['tasks']:
        print("Tasks sorted by title:")
        for task in sort_result['tasks']:
            print(f"  - '{task.title}'")
    
    # Test 5: Project filtering
    projects = storage.get_projects()
    if projects:
        test_project = projects[0]
        print(f"\n5. Testing project filtering (project: {test_project.name}):")
        project_result = storage.list_tasks(project_id=test_project.id)
        print(f"Found {project_result['total']} tasks in project '{test_project.name}'")
    
    # Test 6: Pagination
    print("\n6. Testing pagination (page 2, limit 3):")
    page2_result = storage.list_tasks(skip=3, limit=3)
    print(f"Page 2 info: page={page2_result['page']}, has_prev={page2_result['has_prev']}, has_next={page2_result['has_next']}")
    
    # Test 7: Complex filtering
    print("\n7. Testing complex filtering (status='todo' AND search='test'):")
    complex_result = storage.list_tasks(status="todo", search="test", limit=10)
    print(f"Found {complex_result['total']} tasks with status='todo' containing 'test'")
    
    print("\n=== ENHANCED LISTING TESTS COMPLETED ===")

if __name__ == "__main__":
    test_enhanced_listing()