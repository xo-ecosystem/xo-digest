#!/usr/bin/env python3
"""
Batch fix Fabric task modules in xo_core/fab_tasks/

Ensures all @task decorated functions are properly registered to ns collections
for compatibility with xo-fab --list and fabfile.py namespace chaining.
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Set, Tuple


def should_skip_file(file_path: Path) -> bool:
    """Skip utility files, shared data, and non-task files."""
    skip_patterns = [
        '_shared_data.py',
        'module_utils.py',
        'pin_helpers.py',
        '__init__.py',
        'utils/',
        'constants',
        'shared',
    ]
    
    file_str = str(file_path)
    return any(pattern in file_str for pattern in skip_patterns)


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


def has_ns_collection(content: str) -> bool:
    """Check if file already has an ns collection defined."""
    return 'ns = Collection(' in content or 'ns = Collection()' in content


def get_collection_name(file_path: Path) -> str:
    """Get appropriate collection name based on file path."""
    # For nested files like tools/foo.py, use "foo"
    if file_path.parent.name not in ['fab_tasks', 'pulse', 'vault', 'tools']:
        return file_path.stem
    
    # For files in subdirectories, use the subdirectory name
    if file_path.parent.name in ['pulse', 'vault', 'tools']:
        return file_path.parent.name
    
    # For root fab_tasks files, use the file stem
    return file_path.stem


def generate_ns_code(task_functions: List[str], collection_name: str) -> str:
    """Generate the ns collection code to append to the file."""
    if not task_functions:
        return ""
    
    lines = [
        "",
        "from invoke import Collection",
        f"ns = Collection(\"{collection_name}\")"
    ]
    
    for func_name in task_functions:
        lines.append(f"ns.add_task({func_name}, name=\"{func_name}\")")
    
    return "\n".join(lines)


def fix_file(file_path: Path) -> bool:
    """Fix a single file by adding proper ns collection."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Skip if already has ns collection
        if has_ns_collection(content):
            return False
        
        # Find task functions
        task_functions = find_task_functions(content)
        if not task_functions:
            return False
        
        # Generate and append ns code
        collection_name = get_collection_name(file_path)
        ns_code = generate_ns_code(task_functions, collection_name)
        
        if ns_code:
            # Ensure invoke import is present
            if 'from invoke import' not in content:
                # Find the first import line and add invoke import
                lines = content.split('\n')
                import_index = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_index = i + 1
                    elif line.strip() and not line.strip().startswith('#'):
                        break
                
                invoke_import = "from invoke import task, Collection"
                lines.insert(import_index, invoke_import)
                content = '\n'.join(lines)
            
            # Append ns code
            content += ns_code
            
            # Write back to file
            file_path.write_text(content, encoding='utf-8')
            return True
            
    except Exception as e:
        print(f"⚠️ Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to fix all Fabric task modules."""
    fab_tasks_dir = Path("src/xo_core/fab_tasks")
    
    if not fab_tasks_dir.exists():
        print(f"❌ Directory not found: {fab_tasks_dir}")
        return
    
    fixed_files = []
    skipped_files = []
    error_files = []
    
    # Find all Python files
    for py_file in fab_tasks_dir.rglob("*.py"):
        if should_skip_file(py_file):
            skipped_files.append(py_file)
            continue
        
        print(f"🔍 Checking: {py_file.relative_to(fab_tasks_dir)}")
        
        try:
            if fix_file(py_file):
                fixed_files.append(py_file)
                print(f"✅ Fixed: {py_file.relative_to(fab_tasks_dir)}")
            else:
                print(f"⏭️ Skipped (no changes needed): {py_file.relative_to(fab_tasks_dir)}")
        except Exception as e:
            error_files.append((py_file, str(e)))
            print(f"❌ Error: {py_file.relative_to(fab_tasks_dir)} - {e}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"✅ Fixed: {len(fixed_files)} files")
    print(f"⏭️ Skipped: {len(skipped_files)} files")
    print(f"❌ Errors: {len(error_files)} files")
    
    if fixed_files:
        print(f"\n✅ Fixed files:")
        for file in fixed_files:
            print(f"  - {file.relative_to(fab_tasks_dir)}")
    
    if error_files:
        print(f"\n❌ Files with errors:")
        for file, error in error_files:
            print(f"  - {file.relative_to(fab_tasks_dir)}: {error}")


if __name__ == "__main__":
    main() 