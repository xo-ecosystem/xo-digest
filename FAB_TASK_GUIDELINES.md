# ✅ Fabric Namespace Module Rules

## 🎯 Overview

This document defines the standardized pattern for creating Fabric task modules in the XO Core ecosystem. Following these guidelines ensures consistent, maintainable, and testable task organization.

## 📋 **Core Requirements**

### 1. **Namespace Structure**

```python
from invoke import Collection, task

@task
def my_task(c, param1=None, param2=False):
    """Task description with docstring."""
    # Task implementation
    pass

# Create namespace - MUST be named "ns"
ns = Collection("module_name")
ns.add_task(my_task, "task_alias")
```

### 2. **Import Pattern**

- **Each `fab_tasks/*.py` must expose `ns = Collection("<name>")`**
- **No circular imports** - All internal imports must be inside tasks
- **Use `add_task()` with short aliases** for clarity
- **Ensure testability** via CLI with `fab --list` and task-level `--help`

### 3. **Task Definition Rules**

```python
@task
def task_name(c, param1=None, param2=False, dry_run=False):
    """
    Task description.

    Args:
        param1: Description of param1
        param2: Description of param2
        dry_run: Only show what would happen, don't perform actions
    """
    # Implementation
    pass
```

## 🔧 **Module Examples**

### **DNS Module** (`fab_tasks/dns_check_21xo.py`)

```python
from invoke import Collection, task

@task
def check_dns(c, dry_run=False, validate_resolution=True):
    """Check DNS configuration."""
    # Implementation
    pass

@task
def generate_dns_history(c):
    """Generate DNS history artifacts."""
    # Implementation
    pass

# Create namespace
ns = Collection("dns")
ns.add_task(check_dns, "check")
ns.add_task(generate_dns_history, "history")
```

### **Deploy Module** (`fab_tasks/deploy.py`)

```python
from invoke import Collection, task

@task
def deploy_fly(c, app_name="vault-21xo", dry_run=False):
    """Deploy to Fly.io."""
    # Implementation
    pass

@task
def health_check(c, service="vault"):
    """Health check for service."""
    # Implementation
    pass

# Create namespace
ns = Collection("deploy")
ns.add_task(deploy_fly, "fly")
ns.add_task(health_check, "health")
```

## 🚀 **Main Fabfile Integration**

### **Import Pattern**

```python
# fabfile.py
from invoke import Collection, task

# Import task modules with proper namespace structure
from fab_tasks.dns_check_21xo import ns as dns_ns
from fab_tasks.deploy import ns as deploy_ns
from fab_tasks.patch import ns as patch_ns

# Main namespace
ns = Collection()
ns.add_collection(dns_ns)
ns.add_collection(deploy_ns)
ns.add_collection(patch_ns)
```

## 🧪 **Testing & Validation**

### **CLI Commands to Test**

```bash
# List all available tasks
fab --list

# Test specific task help
fab dns.check --help
fab deploy.health --help

# Test task execution
fab dns.check --dry-run
fab deploy.health --service=vault
```

### **Validation Checklist**

- [ ] **`fab --list`** shows all tasks with correct namespaces
- [ ] **`fab namespace.task --help`** shows proper help text
- [ ] **No import errors** when importing the module
- [ ] **Tasks execute** without runtime errors
- [ ] **Namespace structure** follows the pattern

## 🚨 **Common Issues & Fixes**

### **Issue: Circular Import Error**

```python
# ❌ WRONG - Import at module level
from fab_tasks.deploy import deploy_fly

# ✅ CORRECT - Import inside task
@task
def my_task(c):
    from fab_tasks.deploy import deploy_fly
    deploy_fly(c)
```

### **Issue: Wrong Namespace Name**

```python
# ❌ WRONG
dns_ns = Collection("dns")

# ✅ CORRECT
ns = Collection("dns")
```

### **Issue: Missing Task Registration**

```python
# ❌ WRONG - Task defined but not registered
@task
def my_task(c):
    pass

# ✅ CORRECT - Task registered to namespace
@task
def my_task(c):
    pass

ns = Collection("module")
ns.add_task(my_task, "task")
```

## 📝 **Documentation Standards**

### **Task Docstrings**

```python
@task
def task_name(c, param1=None, dry_run=False):
    """
    Brief description of what the task does.

    Args:
        param1 (str): Description of parameter
        dry_run (bool): Only show what would happen, don't perform actions

    Returns:
        dict: Result summary or None
    """
    pass
```

### **Module Header**

```python
"""
DNS Management Tasks

This module provides tasks for:
- DNS record validation
- CNAME management
- DNS history tracking
- Chart generation
"""
```

## 🔄 **Migration Guide**

### **From Old Pattern to New**

```python
# OLD PATTERN
from invoke import Collection, task

@task
def old_task(c):
    pass

# Create collections
old_ns = Collection("old")
old_ns.add_task(old_task, "task")

# NEW PATTERN
from invoke import Collection, task

@task
def new_task(c):
    pass

# Create namespace
ns = Collection("new")
ns.add_task(new_task, "task")
```

## ✅ **Enforcement**

### **Pre-commit Checks**

- [ ] All `fab_tasks/*.py` files follow the namespace pattern
- [ ] No circular imports exist
- [ ] All tasks are properly registered
- [ ] CLI commands work as expected

### **Code Review Checklist**

- [ ] Namespace structure follows guidelines
- [ ] Tasks have proper docstrings
- [ ] No circular imports
- [ ] Tasks are testable via CLI
- [ ] Integration with main fabfile works

---

**🌌 Follow these guidelines to maintain cosmic alignment across all Fabric tasks!**
