#!/usr/bin/env python3
"""
Auto-generate .cursor/tasks.json from chain.py files and @task functions.

This script scans all chain.py files and @task functions to create a comprehensive
task index for Cursor agent support.
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set


def find_task_functions(content: str) -> List[str]:
    """Find all @task decorated functions in the file."""
    try:
        tree = ast.parse(content)
        task_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has @task decorator
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'task':
                        task_functions.append(node.name)
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'task':
                        task_functions.append(node.name)
        
        return task_functions
    except SyntaxError:
        # Fallback to regex if AST parsing fails
        task_pattern = r'@task[^\n]*\n\s*def\s+(\w+)'
        matches = re.findall(task_pattern, content)
        return matches


def get_task_docstring(content: str, task_name: str) -> str:
    """Extract docstring for a specific task function."""
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == task_name:
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                    return node.body[0].value.s.strip()
                elif node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                    return str(node.body[0].value.value).strip()
        
        return ""
    except SyntaxError:
        return ""


def scan_chain_files() -> Dict:
    """Scan all chain.py files and extract task information."""
    fab_tasks_dir = Path("src/xo_core/fab_tasks")
    tasks_data = {}
    
    # Find all chain.py files
    chain_files = list(fab_tasks_dir.rglob("chain.py"))
    
    for chain_file in chain_files:
        try:
            content = chain_file.read_text(encoding='utf-8')
            
            # Extract namespace name from chain.py
            namespace_match = re.search(r'ns = Collection\("([^"]+)"\)', content)
            if not namespace_match:
                continue
                
            namespace = namespace_match.group(1)
            
            # Find registered collections
            collection_matches = re.findall(r'ns\.add_collection\([^,]+\.ns, name="([^"]+)"\)', content)
            
            tasks_data[namespace] = {
                "description": f"{namespace.title()} operations",
                "subtasks": {}
            }
            
            # Add registered collections
            for collection_name in collection_matches:
                tasks_data[namespace]["subtasks"][f"{namespace}.{collection_name}"] = {
                    "description": f"{collection_name.replace('-', ' ').title()} operations",
                    "suggestion": f"Use for {collection_name.replace('-', ' ')} operations",
                    "category": "utility"
                }
            
        except Exception as e:
            print(f"⚠️ Error scanning {chain_file}: {e}")
    
    return tasks_data


def scan_task_files() -> Dict:
    """Scan all task files for @task functions."""
    fab_tasks_dir = Path("src/xo_core/fab_tasks")
    task_functions = {}
    
    # Find all Python files with @task
    for py_file in fab_tasks_dir.rglob("*.py"):
        if py_file.name in ['__init__.py', 'chain.py'] or 'utils' in str(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            
            if '@task' not in content:
                continue
                
            tasks = find_task_functions(content)
            
            if tasks:
                # Determine namespace from file path
                if py_file.parent.name in ['pulse', 'vault', 'tools', 'inbox', 'utils', 'tunnel', 'service_manager', 'cloudflare_utils', 'cosmic', 'doctor']:
                    namespace = py_file.parent.name
                else:
                    namespace = py_file.stem
                
                if namespace not in task_functions:
                    task_functions[namespace] = {}
                
                for task_name in tasks:
                    docstring = get_task_docstring(content, task_name)
                    task_functions[namespace][task_name] = {
                        "description": docstring or f"{task_name.replace('_', ' ').title()} operation",
                        "suggestion": f"Use for {task_name.replace('_', ' ')} operations",
                        "category": "utility"
                    }
                    
        except Exception as e:
            print(f"⚠️ Error scanning {py_file}: {e}")
    
    return task_functions


def generate_categories() -> Dict:
    """Generate category definitions."""
    return {
        "automation": "Automated workflows and chains",
        "content": "Content creation and management",
        "storage": "Storage and archival operations",
        "development": "Development and coding tools",
        "preview": "Preview and rendering operations",
        "publishing": "Publishing and distribution",
        "review": "Review and approval processes",
        "security": "Security and signing operations",
        "sync": "Synchronization operations",
        "testing": "Testing and validation",
        "nft": "NFT and blockchain operations",
        "export": "Export and conversion operations",
        "documentation": "Documentation generation",
        "diagnostics": "Diagnostic and troubleshooting",
        "quality": "Code quality and linting",
        "generation": "Code and content generation",
        "utility": "Utility and helper functions",
        "pulse": "Pulse-specific operations",
        "notifications": "Notification and messaging",
        "services": "Service management",
        "networking": "Network and tunnel operations",
        "cloudflare": "Cloudflare-specific operations",
        "cosmic": "Cosmic operations"
    }


def generate_workflows() -> Dict:
    """Generate common workflow definitions."""
    return {
        "pulse-publishing": [
            "pulse.new",
            "pulse.preview",
            "pulse.review",
            "pulse.sign",
            "pulse.archive",
            "pulse.publish"
        ],
        "vault-automation": [
            "vault.auto"
        ],
        "development-setup": [
            "tools.cursor",
            "tools.lint",
            "tools.doctor"
        ],
        "content-creation": [
            "pulse.new",
            "pulse.preview",
            "pulse.export-html"
        ]
    }


def main():
    """Main function to generate tasks.json."""
    print("🔍 Scanning chain.py files...")
    chain_tasks = scan_chain_files()
    
    print("🔍 Scanning task files...")
    file_tasks = scan_task_files()
    
    # Merge tasks
    all_tasks = chain_tasks.copy()
    
    for namespace, tasks in file_tasks.items():
        if namespace not in all_tasks:
            all_tasks[namespace] = {
                "description": f"{namespace.title()} operations",
                "subtasks": {}
            }
        
        for task_name, task_info in tasks.items():
            all_tasks[namespace]["subtasks"][f"{namespace}.{task_name}"] = task_info
    
    # Generate final structure
    tasks_json = {
        "tasks": all_tasks,
        "categories": generate_categories(),
        "workflows": generate_workflows()
    }
    
    # Write to .cursor/tasks.json
    output_path = Path(".cursor/tasks.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tasks_json, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {output_path}")
    print(f"📊 Found {len(all_tasks)} namespaces")
    
    total_tasks = sum(len(ns['subtasks']) for ns in all_tasks.values())
    print(f"📋 Total tasks: {total_tasks}")


if __name__ == "__main__":
    main() 