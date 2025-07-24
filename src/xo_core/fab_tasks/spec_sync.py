"""
Spec Manifest Sync Task
Automatically scans all fab_tasks and updates spec_manifest.mdx
"""

import os
import re
import ast
from pathlib import Path
from datetime import datetime
from invoke import task
from invoke import Collection

@task
def sync_manifest(c):
    """Scan all fab_tasks and update spec_manifest.mdx with implemented tasks"""
    print("🔄 Syncing spec manifest with implemented tasks...")
    
    # Scan all task files
    task_files = scan_task_files()
    
    # Extract task information
    tasks = extract_tasks(task_files)
    
    # Update spec manifest
    update_spec_manifest(tasks)
    
    print("✅ Spec manifest synced successfully!")

def scan_task_files():
    """Scan all Python files in fab_tasks directory"""
    fab_tasks_dir = Path("src/xo_core/fab_tasks")
    task_files = []
    
    for py_file in fab_tasks_dir.rglob("*.py"):
        if py_file.name != "__init__.py":
            task_files.append(py_file)
    
    return task_files

def extract_tasks(task_files):
    """Extract task information from Python files"""
    tasks = {}
    
    for file_path in task_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse the file
            tree = ast.parse(content)
            
            # Find @task decorators and function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has @task decorator
                    if has_task_decorator(node):
                        task_info = extract_task_info(node, file_path)
                        if task_info:
                            namespace = task_info['namespace']
                            if namespace not in tasks:
                                tasks[namespace] = []
                            tasks[namespace].append(task_info)
        
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
    
    return tasks

def has_task_decorator(node):
    """Check if function has @task decorator"""
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name) and decorator.func.id == 'task':
                return True
        elif isinstance(decorator, ast.Name) and decorator.id == 'task':
            return True
    return False

def extract_task_info(node, file_path):
    """Extract task information from function definition"""
    # Get namespace from file path
    namespace = determine_namespace(file_path)
    
    # Get task name
    task_name = node.name
    
    # Get docstring
    docstring = ast.get_docstring(node) or "No description available"
    
    # Check if task is implemented (has function body)
    is_implemented = len(node.body) > 0 and not (
        len(node.body) == 1 and 
        isinstance(node.body[0], ast.Pass)
    )
    
    return {
        'namespace': namespace,
        'name': task_name,
        'description': docstring,
        'implemented': is_implemented,
        'file': str(file_path)
    }

def determine_namespace(file_path):
    """Determine namespace from file path"""
    path_parts = file_path.parts
    
    # Check for specific namespace files
    if 'backend_tasks.py' in path_parts:
        return 'backend'
    elif 'storage_tasks.py' in path_parts:
        return 'storage'
    elif 'sign_tasks.py' in path_parts:
        return 'sign'
    elif 'seal_tasks.py' in path_parts:
        return 'seal'
    elif 'cosmos_tasks.py' in path_parts:
        return 'cosmos'
    elif 'vault' in path_parts:
        return 'vault'
    elif 'pulse' in path_parts:
        return 'pulse'
    elif 'digest' in path_parts:
        return 'digest'
    else:
        # Default namespace based on directory
        for part in path_parts:
            if part in ['backend', 'storage', 'vault', 'pulse', 'digest', 'cosmos']:
                return part
        return 'misc'

def update_spec_manifest(tasks):
    """Update spec_manifest.mdx with task information"""
    spec_path = Path("src/xo_core/fab_tasks/spec_manifest.mdx")
    
    if not spec_path.exists():
        print("❌ spec_manifest.mdx not found!")
        return
    
    # Read current spec
    with open(spec_path, 'r') as f:
        content = f.read()
    
    # Update last_synced timestamp
    content = update_last_synced(content)
    
    # Update each namespace section
    for namespace, namespace_tasks in tasks.items():
        content = update_namespace_section(content, namespace, namespace_tasks)
    
    # Write updated spec
    with open(spec_path, 'w') as f:
        f.write(content)

def update_last_synced(content):
    """Update last_synced timestamp in frontmatter"""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Update or add last_synced in frontmatter
    if 'last_synced:' in content:
        content = re.sub(
            r'last_synced: "[^"]*"',
            f'last_synced: "{timestamp}"',
            content
        )
    else:
        # Add last_synced after tags
        content = re.sub(
            r'(tags: \[[^\]]*\])',
            f'\\1\nlast_synced: "{timestamp}"',
            content
        )
    
    return content

def update_namespace_section(content, namespace, tasks):
    """Update a specific namespace section in the spec"""
    # Find the namespace section
    section_pattern = rf'### .*`{namespace}`.*Namespace.*\n\n\|.*\n\|.*\n\|.*\n'
    section_match = re.search(section_pattern, content, re.MULTILINE | re.DOTALL)
    
    if section_match:
        # Update existing section
        old_section = section_match.group(0)
        new_section = generate_namespace_section(namespace, tasks)
        content = content.replace(old_section, new_section)
    else:
        # Add new section
        new_section = generate_namespace_section(namespace, tasks)
        content += f"\n\n{new_section}"
    
    return content

def generate_namespace_section(namespace, tasks):
    """Generate markdown table for namespace tasks"""
    # Determine if namespace is implemented
    implemented_tasks = [t for t in tasks if t['implemented']]
    status_icon = "✅ IMPLEMENTED" if implemented_tasks else "⏳ PLANNED"
    
    section = f"### 🛠️ `{namespace}` Namespace {status_icon}\n\n"
    section += "| Task | Description | Status |\n"
    section += "| ---- | ----------- | ------ |\n"
    
    for task in tasks:
        status = "✅" if task['implemented'] else "⏳"
        section += f"| `{namespace}.{task['name']}` | {task['description']} | {status} |\n"
    
    return section

# Create spec namespace
spec_ns = Collection("spec")
spec_ns.add_task(sync_manifest, name="sync_manifest") 