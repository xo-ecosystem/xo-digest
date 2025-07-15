#!/usr/bin/env python3
"""
XO Fabric Task Discovery Tool

This script helps users discover and understand available xo-fab tasks,
providing search, categorization, and workflow guidance.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


def load_tasks_json() -> Dict:
    """Load the tasks.json file."""
    tasks_path = Path(".cursor/tasks.json")
    if not tasks_path.exists():
        print("❌ .cursor/tasks.json not found. Run scripts/generate_tasks_json.py first.")
        sys.exit(1)
    
    with open(tasks_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def search_tasks(tasks_data: Dict, query: str) -> List[Dict]:
    """Search for tasks matching the query."""
    results = []
    query_lower = query.lower()
    
    for namespace, namespace_data in tasks_data["tasks"].items():
        if query_lower in namespace.lower():
            results.append({
                "type": "namespace",
                "name": namespace,
                "description": namespace_data["description"],
                "subtasks": list(namespace_data["subtasks"].keys())
            })
        
        for task_name, task_data in namespace_data["subtasks"].items():
            if (query_lower in task_name.lower() or 
                query_lower in task_data["description"].lower() or
                query_lower in task_data["suggestion"].lower()):
                results.append({
                    "type": "task",
                    "name": task_name,
                    "description": task_data["description"],
                    "suggestion": task_data["suggestion"],
                    "category": task_data["category"]
                })
    
    return results


def show_task_details(tasks_data: Dict, task_name: str) -> None:
    """Show detailed information about a specific task."""
    for namespace, namespace_data in tasks_data["tasks"].items():
        if task_name in namespace_data["subtasks"]:
            task_data = namespace_data["subtasks"][task_name]
            print(f"\n📋 Task: {task_name}")
            print(f"📝 Description: {task_data['description']}")
            print(f"💡 Suggestion: {task_data['suggestion']}")
            print(f"🏷️ Category: {task_data['category']}")
            
            # Show related workflows
            related_workflows = []
            for workflow_name, workflow_steps in tasks_data["workflows"].items():
                if task_name in workflow_steps:
                    related_workflows.append(workflow_name)
            
            if related_workflows:
                print(f"🔄 Related workflows: {', '.join(related_workflows)}")
            return
    
    print(f"❌ Task '{task_name}' not found.")


def list_by_category(tasks_data: Dict, category: Optional[str] = None) -> None:
    """List tasks by category."""
    categories = {}
    
    for namespace, namespace_data in tasks_data["tasks"].items():
        for task_name, task_data in namespace_data["subtasks"].items():
            cat = task_data["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(task_name)
    
    if category:
        if category in categories:
            print(f"\n📂 Category: {category}")
            print(f"📖 Description: {tasks_data['categories'][category]}")
            print("\nTasks:")
            for task in sorted(categories[category]):
                print(f"  - {task}")
        else:
            print(f"❌ Category '{category}' not found.")
            print(f"Available categories: {', '.join(sorted(categories.keys()))}")
    else:
        print("\n📂 Available Categories:")
        for cat in sorted(categories.keys()):
            print(f"  - {cat}: {len(categories[cat])} tasks")


def show_workflows(tasks_data: Dict, workflow_name: Optional[str] = None) -> None:
    """Show available workflows."""
    if workflow_name:
        if workflow_name in tasks_data["workflows"]:
            print(f"\n🔄 Workflow: {workflow_name}")
            print(f"📝 Description: {tasks_data.get('workflows', {}).get(workflow_name, 'No description available')}")
            print("\nSteps:")
            for step in tasks_data["workflows"][workflow_name]:
                print(f"  - {step}")
        else:
            print(f"❌ Workflow '{workflow_name}' not found.")
            print(f"Available workflows: {', '.join(tasks_data['workflows'].keys())}")
    else:
        print("\n🔄 Available Workflows:")
        for workflow in sorted(tasks_data["workflows"].keys()):
            print(f"  - {workflow}")


def show_namespace_summary(tasks_data: Dict, namespace: Optional[str] = None) -> None:
    """Show namespace summary."""
    if namespace:
        if namespace in tasks_data["tasks"]:
            ns_data = tasks_data["tasks"][namespace]
            print(f"\n📦 Namespace: {namespace}")
            print(f"📝 Description: {ns_data['description']}")
            print(f"📋 Tasks: {len(ns_data['subtasks'])}")
            print("\nAvailable tasks:")
            for task_name in sorted(ns_data["subtasks"].keys()):
                print(f"  - {task_name}")
        else:
            print(f"❌ Namespace '{namespace}' not found.")
            print(f"Available namespaces: {', '.join(tasks_data['tasks'].keys())}")
    else:
        print("\n📦 Available Namespaces:")
        for ns in sorted(tasks_data["tasks"].keys()):
            task_count = len(tasks_data["tasks"][ns]["subtasks"])
            print(f"  - {ns}: {task_count} tasks")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("🔍 XO Fabric Task Discovery Tool")
        print("\nUsage:")
        print("  python scripts/task_discovery.py search <query>")
        print("  python scripts/task_discovery.py task <task-name>")
        print("  python scripts/task_discovery.py category [category-name]")
        print("  python scripts/task_discovery.py workflow [workflow-name]")
        print("  python scripts/task_discovery.py namespace [namespace-name]")
        print("  python scripts/task_discovery.py summary")
        return
    
    tasks_data = load_tasks_json()
    command = sys.argv[1]
    
    if command == "search" and len(sys.argv) >= 3:
        query = sys.argv[2]
        results = search_tasks(tasks_data, query)
        
        if results:
            print(f"\n🔍 Search results for '{query}':")
            for result in results:
                if result["type"] == "namespace":
                    print(f"\n📦 {result['name']}: {result['description']}")
                    print(f"   Tasks: {', '.join(result['subtasks'])}")
                else:
                    print(f"\n📋 {result['name']}")
                    print(f"   Description: {result['description']}")
                    print(f"   Category: {result['category']}")
        else:
            print(f"❌ No results found for '{query}'")
    
    elif command == "task" and len(sys.argv) >= 3:
        task_name = sys.argv[2]
        show_task_details(tasks_data, task_name)
    
    elif command == "category":
        category = sys.argv[2] if len(sys.argv) >= 3 else None
        list_by_category(tasks_data, category)
    
    elif command == "workflow":
        workflow = sys.argv[2] if len(sys.argv) >= 3 else None
        show_workflows(tasks_data, workflow)
    
    elif command == "namespace":
        namespace = sys.argv[2] if len(sys.argv) >= 3 else None
        show_namespace_summary(tasks_data, namespace)
    
    elif command == "summary":
        total_tasks = sum(len(ns['subtasks']) for ns in tasks_data["tasks"].values())
        total_namespaces = len(tasks_data["tasks"])
        total_workflows = len(tasks_data["workflows"])
        
        print(f"\n📊 XO Fabric Task Summary:")
        print(f"📦 Namespaces: {total_namespaces}")
        print(f"📋 Total Tasks: {total_tasks}")
        print(f"🔄 Workflows: {total_workflows}")
        print(f"🏷️ Categories: {len(tasks_data['categories'])}")
        
        print(f"\n📦 Top Namespaces:")
        namespace_counts = [(ns, len(data['subtasks'])) for ns, data in tasks_data["tasks"].items()]
        namespace_counts.sort(key=lambda x: x[1], reverse=True)
        
        for ns, count in namespace_counts[:5]:
            print(f"  - {ns}: {count} tasks")
    
    else:
        print("❌ Invalid command. Use 'python scripts/task_discovery.py' for help.")


if __name__ == "__main__":
    main() 