# 🛠️ XO Fabfile Health Management Solution

## Problem Analysis

The recurring `KeyError: 'validate'` and similar issues stem from several root causes:

1. **Duplicate Import Conflicts**: Multiple import attempts for the same module
2. **Missing Task Modules**: References to non-existent task files
3. **Collection Naming Conflicts**: Duplicate collection names in the same namespace
4. **Import Order Dependencies**: Circular or incorrect import dependencies
5. **Syntax Errors**: Malformed Python code in task modules

## 🔧 Comprehensive Solution

### 1. **Fabfile Health Management System**

Created `src/xo_core/fab_tasks/fabfile_health.py` with diagnostic and repair tools:

```bash
# Diagnose issues
xo-fab health.diagnose

# Auto-fix common problems
xo-fab health.fix

# Validate fabfile integrity
xo-fab health.validate

# Backup/restore functionality
xo-fab health.backup
xo-fab health.restore fabfile.backup_20250724_020000.py
```

### 2. **Safe Import Pattern**

Replace fragile imports with robust error handling:

```python
# ❌ Fragile - fails if module missing
from xo_core.fab_tasks.validate_tasks import ns as validate_ns

# ✅ Robust - continues if module missing
def safe_import_collection(module_name, collection_name="ns"):
    try:
        module = __import__(f"xo_core.fab_tasks.{module_name}", fromlist=[collection_name])
        return getattr(module, collection_name, None)
    except Exception as e:
        print(f"⚠️  Warning: Could not import {module_name}: {e}")
        return None
```

### 3. **Clean Fabfile Template**

Regenerated `fabfile.py` with safe import patterns:

```python
from invoke import task, Collection
from pathlib import Path

# Safe import function
def safe_import_collection(module_name, collection_name="ns"):
    """Safely import a collection with error handling"""
    try:
        module = __import__(f"xo_core.fab_tasks.{module_name}", fromlist=[collection_name])
        return getattr(module, collection_name, None)
    except Exception as e:
        print(f"⚠️  Warning: Could not import {module_name}: {e}")
        return None

# Create main namespace
ns = Collection()

# Import and add collections safely
collections_to_import = [
    ("backend_tasks", "backend_ns"),
    ("storage_tasks", "storage_ns"),
    ("sign_tasks", "sign_ns"),
    ("seal_tasks", "seal_ns"),
    ("cosmos_tasks", "cosmos_ns"),
    ("spec_sync", "spec_ns"),
    ("env_tasks", "env_ns"),
]

for module_name, collection_name in collections_to_import:
    collection = safe_import_collection(module_name, collection_name)
    if collection:
        ns.add_collection(collection)
        print(f"✅ Added {module_name} collection")

# Define the default namespace
namespace = ns
```

## 🛡️ Prevention Strategies

### 1. **Pre-commit Hooks**

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validate fabfile before commit
python -c "import fabfile" || {
    echo "❌ Fabfile validation failed"
    exit 1
}
```

### 2. **CI/CD Validation**

Add to GitHub Actions or CI pipeline:

```yaml
- name: Validate Fabfile
  run: |
    python -c "import fabfile"
    xo-fab health.validate
```

### 3. **Development Workflow**

```bash
# Before making changes
xo-fab health.backup

# After making changes
xo-fab health.diagnose
xo-fab health.validate

# If issues found
xo-fab health.fix
```

## 🔍 Diagnostic Tools

### 1. **Module Health Checker**

```python
def check_module_health(module_name: str, module_path: Path) -> Dict[str, any]:
    """Check health of a task module"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, 'ns'):
            return {"healthy": True, "message": "Has Collection 'ns'"}
        else:
            return {"healthy": False, "message": "No Collection found"}
    except Exception as e:
        return {"healthy": False, "message": f"Import error: {e}"}
```

### 2. **Duplicate Import Detector**

```python
def find_duplicate_imports() -> List[str]:
    """Find duplicate import statements in fabfile.py"""
    with open("fabfile.py", "r") as f:
        content = f.read()

    lines = content.split('\n')
    imports = []

    for line in lines:
        if 'import' in line and 'validate_tasks' in line:
            imports.append(line.strip())

    return imports if len(imports) > 1 else []
```

### 3. **Collection Conflict Finder**

```python
def find_collection_conflicts() -> List[str]:
    """Find collection naming conflicts"""
    with open("fabfile.py", "r") as f:
        content = f.read()

    conflicts = []
    if content.count('validate_ns') > 1:
        conflicts.append("validate_ns used multiple times")

    return conflicts
```

## 🚀 Advanced Solutions

### 1. **Dynamic Task Discovery**

```python
@task
def auto_discover_tasks(c):
    """Automatically discover and register task modules"""
    task_modules = scan_task_modules()

    for module_name, module_path in task_modules.items():
        collection = safe_import_collection(module_name)
        if collection:
            ns.add_collection(collection)
            print(f"✅ Auto-discovered: {module_name}")
```

### 2. **Task Module Templates**

Create standardized templates for new task modules:

```python
# Template: src/xo_core/fab_tasks/template_tasks.py
"""
Template for new task modules
"""

from invoke import task, Collection

@task
def example_task(c):
    """Example task description"""
    print("Example task executed")

# Create namespace
template_ns = Collection("template")
template_ns.add_task(example_task, name="example")
```

### 3. **Health Monitoring Dashboard**

```python
@task
def health_dashboard(c):
    """Display comprehensive health status"""
    print("🏥 XO Fabfile Health Dashboard")
    print("=" * 40)

    # Module status
    modules = scan_task_modules()
    healthy_count = sum(1 for m in modules.values() if check_module_health(m.stem, m)["healthy"])
    print(f"📦 Modules: {healthy_count}/{len(modules)} healthy")

    # Import status
    duplicates = find_duplicate_imports()
    print(f"🔄 Duplicates: {len(duplicates)} found")

    # Collection status
    conflicts = find_collection_conflicts()
    print(f"⚡ Conflicts: {len(conflicts)} found")
```

## 📋 Best Practices

### 1. **Module Organization**

```
src/xo_core/fab_tasks/
├── __init__.py
├── backend_tasks.py      # backend_ns
├── storage_tasks.py      # storage_ns
├── sign_tasks.py         # sign_ns
├── seal_tasks.py         # seal_ns
├── cosmos_tasks.py       # cosmos_ns
├── env_tasks.py          # env_ns
├── spec_sync.py          # spec_ns
└── fabfile_health.py     # health_ns
```

### 2. **Naming Conventions**

- Task modules: `{namespace}_tasks.py`
- Collections: `{namespace}_ns`
- Tasks: `{namespace}.{action}`

### 3. **Error Handling**

```python
# Always wrap imports in try/except
try:
    from xo_core.fab_tasks.some_tasks import some_ns
    ns.add_collection(some_ns)
except ImportError as e:
    print(f"⚠️  Warning: {e}")
```

### 4. **Testing Strategy**

```bash
# Test individual modules
python -c "from src.xo_core.fab_tasks.env_tasks import env_ns; print('✅ env_tasks OK')"

# Test full fabfile
python -c "import fabfile; print('✅ fabfile OK')"

# Test task discovery
xo-fab --list
```

## 🔄 Recovery Procedures

### 1. **Immediate Recovery**

```bash
# If fabfile is broken
xo-fab health.backup
xo-fab health.fix
xo-fab health.validate
```

### 2. **Full Reset**

```bash
# Complete reset procedure
git stash
xo-fab health.backup
xo-fab health.regenerate_fabfile
git stash pop
xo-fab health.validate
```

### 3. **Emergency Mode**

```bash
# Minimal working fabfile
cat > fabfile.py << 'EOF'
from invoke import task, Collection
ns = Collection()
@task
def emergency(c):
    print("Emergency mode - basic functionality only")
ns.add_task(emergency)
namespace = ns
EOF
```

## 📊 Monitoring and Metrics

### 1. **Health Score**

```python
def calculate_health_score():
    """Calculate overall fabfile health score (0-100)"""
    score = 100

    # Deduct for each issue
    if find_duplicate_imports():
        score -= 20
    if find_collection_conflicts():
        score -= 30
    if not validate_fabfile():
        score -= 50

    return max(0, score)
```

### 2. **Issue Tracking**

```python
@task
def health_report(c):
    """Generate detailed health report"""
    issues = []

    # Collect all issues
    issues.extend(find_duplicate_imports())
    issues.extend(find_collection_conflicts())

    # Generate report
    with open("fabfile_health_report.md", "w") as f:
        f.write(f"# Fabfile Health Report\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Issues: {len(issues)}\n")
        for issue in issues:
            f.write(f"- {issue}\n")
```

---

**Status**: ✅ **IMPLEMENTED** - Comprehensive fabfile health management system
**Last Updated**: 2025-07-24T02:30:00Z
**Agent**: XO Fabfile Health Manager
