#!/usr/bin/env python3
"""
Quick fix for Fabric task modules - ensures all @task functions are registered to ns collections.
Run with: python scripts/fix_fabric_tasks_simple.py
"""

import re
from pathlib import Path

def fix_fabric_tasks():
    fab_tasks_dir = Path("src/xo_core/fab_tasks")
    fixed_count = 0
    
    for py_file in fab_tasks_dir.rglob("*.py"):
        # Skip utility files
        if any(skip in str(py_file) for skip in ['_shared_data.py', '__init__.py', 'utils/', 'constants']):
            continue
            
        try:
            content = py_file.read_text()
            
            # Skip if already has ns collection
            if 'ns = Collection(' in content:
                continue
                
            # Find @task functions
            task_pattern = r'@task[^\n]*\n\s*def\s+(\w+)'
            tasks = re.findall(task_pattern, content)
            
            if not tasks:
                continue
                
            # Generate collection name
            collection_name = py_file.stem
            if py_file.parent.name in ['pulse', 'vault', 'tools']:
                collection_name = py_file.parent.name
                
            # Add invoke import if missing
            if 'from invoke import' not in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        lines.insert(i + 1, 'from invoke import task, Collection')
                        break
                content = '\n'.join(lines)
                
            # Add ns collection
            ns_code = f"\n\nfrom invoke import Collection\nns = Collection(\"{collection_name}\")"
            for task in tasks:
                ns_code += f"\nns.add_task({task}, name=\"{task}\")"
                
            py_file.write_text(content + ns_code)
            print(f"✅ Fixed: {py_file.relative_to(fab_tasks_dir)}")
            fixed_count += 1
            
        except Exception as e:
            print(f"⚠️ Error with {py_file}: {e}")
            
    print(f"\n🎉 Fixed {fixed_count} files!")

if __name__ == "__main__":
    fix_fabric_tasks() 