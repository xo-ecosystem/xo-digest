import os
import yaml
import re
from invoke import task, Collection
from pathlib import Path
import pathlib
import ast


@task(help={"fix": "Install missing packages and update requirements.txt"})
def check_packages(c, fix=False):
    """🩺 Check required Python packages for XO FAB tasks."""
    import importlib
    missing = []
    required = [
        "PIL",
        "shutil",
        "pathlib",
        "zipfile",
        "arweave",
        "web3",
        "requests",
        "boto3",
        "tqdm",
        "python-dotenv",
        "aiohttp",
        "pillow",
        "pystorj",
    ]
    for pkg in required:
        try:
            importlib.import_module(pkg.lower())
            print(f"✅ {pkg} available")
        except ImportError:
            missing.append(pkg)
            print(
                f"❌ Missing: {pkg} — install with: pip install {pkg}  # vault-dep"
                if pkg in ["arweave", "web3"]
                else f"❌ Missing: {pkg} — install with: pip install {pkg}"
            )
    if missing:
        pip_line = "pip install " + " ".join(missing)
        print(f"\n📦 To install all missing packages:\n➡️  {pip_line}")

        if fix:
            import subprocess
            print("🛠️ Installing missing packages...")
            subprocess.run(["pip", "install", *missing])

            # Append missing packages to requirements.txt if not present
            req_path = Path("requirements.txt")
            existing = []
            if req_path.exists():
                with open(req_path, "r") as f:
                    existing = f.read().splitlines()

            with open(req_path, "a") as f:
                for pkg in missing:
                    if pkg not in existing:
                        f.write(pkg + "\n")
                        print(f"➕ Added to requirements.txt: {pkg}")


@task
def fix_preview_import(c):
    """Auto-comment broken import from preview.py"""
    init_file = pathlib.Path("src/xo_core/vault/__init__.py")
    text = init_file.read_text()
    if "from .preview import all as preview_all" in text:
        patched = text.replace(
            "from .preview import all as preview_all",
            "# from .preview import all as preview_all  # patched by dev_doctor"
        )
        init_file.write_text(patched)
        print("✅ Patched preview import in vault/__init__.py")
    else:
        print("✅ Nothing to patch.")


# Path to dev_doctor/rules/ at the root of xo-core
RULES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "dev_doctor", "rules"
)

def load_rules():
    """Load all YAML rules from the dev_doctor/rules/ directory."""
    rules = []
    if not os.path.isdir(RULES_DIR):
        print(f"⚠️ Rules directory not found: {RULES_DIR}")
        return rules
    
    for filename in os.listdir(RULES_DIR):
        if filename.endswith((".yml", ".yaml")):
            path = os.path.join(RULES_DIR, filename)
            try:
                with open(path, "r") as f:
                    rule_data = yaml.safe_load(f)
                    if rule_data:
                        # Handle both old and new rule formats
                        if isinstance(rule_data, dict):
                            if 'rule' in rule_data:
                                # New format: single rule with 'rule' key
                                rules.append((filename, rule_data['rule']))
                            elif 'name' in rule_data or 'type' in rule_data:
                                # Old format: direct rule
                                rules.append((filename, rule_data))
                            else:
                                # Check for multi-rule format (multiple YAML documents)
                                print(f"⚠️ Unknown rule format in {filename}")
                        else:
                            print(f"⚠️ Invalid rule format in {filename}")
            except yaml.YAMLError as e:
                print(f"⚠️ Error loading {filename}: {e}")
            except Exception as e:
                print(f"⚠️ Unexpected error loading {filename}: {e}")
    
    return rules

def check_required_function(target_file, required_func):
    """Check if a required function exists in the target file."""
    if not os.path.exists(target_file):
        print(f"❌ Target file not found: {target_file}")
        return False
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for function definition patterns
        patterns = [
            rf"def {re.escape(required_func)}\s*\(",  # Standard function def
            rf"async def {re.escape(required_func)}\s*\(",  # Async function def
            rf"class {re.escape(required_func)}\s*[\(:]",  # Class definition
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        
        print(f"❌ Function '{required_func}' not found in {target_file}")
        return False
        
    except Exception as e:
        print(f"❌ Error reading {target_file}: {e}")
        return False

def check_required_import(target_file, import_statement, fix=False):
    """Check if a required import statement exists in the target file."""
    if not os.path.exists(target_file):
        print(f"❌ Target file not found: {target_file}")
        return False
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if import_statement in content:
            return True
        
        print(f"❌ Import statement not found: {import_statement}")
        if fix:
            print(f"🛠️ Attempting to auto-fix: Adding '{import_statement}' to {target_file}")
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                # Add import after any shebang or module docstring
                insert_at = 0
                for i, line in enumerate(lines):
                    if line.startswith("#!") or line.strip().startswith('"""'):
                        insert_at = i + 1
                    elif line.strip() and not line.strip().startswith("#"):
                        break
                lines.insert(insert_at, import_statement + "\n")
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"✅ Auto-fixed: {target_file}")
                return True
            except Exception as e:
                print(f"❌ Auto-fix failed: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error reading {target_file}: {e}")
        return False

def apply_rule(filename, rule, fix=False):
    """Apply a single rule and return True if it passes, False otherwise."""
    # Handle new rule format
    if 'id' in rule:
        rule_name = rule.get('id', filename)
        print(f"🔍 Checking rule: {rule_name}")
        
        # Handle new format with 'checks' array
        if 'checks' in rule:
            target_file = rule.get('applies_to')
            if not target_file:
                print(f"❌ Invalid rule: missing 'applies_to' field")
                return False
            
            all_checks_passed = True
            for check in rule['checks']:
                check_type = check.get('type')
                if check_type == 'required_function':
                    func_name = check.get('function')
                    if not func_name:
                        print(f"❌ Invalid check: missing 'function' field")
                        all_checks_passed = False
                        continue
                    
                    if not check_required_function(target_file, func_name):
                        all_checks_passed = False
                
                elif check_type == 'import_statement':
                    import_stmt = check.get('import_statement')
                    if not import_stmt:
                        print(f"❌ Invalid check: missing 'import_statement' field")
                        all_checks_passed = False
                        continue
                    
                    if not check_required_import(target_file, import_stmt, fix=fix):
                        all_checks_passed = False
            
            return all_checks_passed
        
        # Handle new format with direct check_type
        check_type = rule.get('check_type')
        target_file = rule.get('target_file')
        
        if check_type == 'import_statement':
            import_statement = rule.get('import_statement')
            if not target_file or not import_statement:
                print(f"❌ Invalid rule: missing target_file or import_statement")
                return False
            return check_required_import(target_file, import_statement, fix=fix)
    
    # Handle old rule format
    else:
        rule_name = rule.get('name', filename)
        print(f"🔍 Checking rule: {rule_name}")
        
        # Handle different rule types
        rule_type = rule.get('type', 'basic')
        
        if rule_type == 'required_function':
            target_file = rule.get('target_file')
            required_func = rule.get('required_function')
            
            if not target_file or not required_func:
                print(f"❌ Invalid rule: missing target_file or required_function")
                return False
            
            return check_required_function(target_file, required_func)
        
        elif rule_type == 'required_import':
            target_file = rule.get('target_file')
            import_statement = rule.get('import_statement')
            
            if not target_file or not import_statement:
                print(f"❌ Invalid rule: missing target_file or import_statement")
                return False
            
            return check_required_import(target_file, import_statement, fix=fix)
        
        elif rule_type == 'file_exists':
            target_file = rule.get('target_file')
            if not target_file:
                print(f"❌ Invalid rule: missing target_file")
                return False
            
            if os.path.exists(target_file):
                print(f"✅ File exists: {target_file}")
                return True
            else:
                print(f"❌ Missing required file: {target_file}")
                return False
        
        else:
            # Legacy basic rule support
            target_file = rule.get('target_file')
            if target_file and not os.path.exists(target_file):
                print(f"❌ Missing required file: {target_file}")
                return False
            
            print("✅ Rule passed")
            return True

@task(help={"verbose": "Enable verbose output", "fix": "Attempt auto-fixes for failed rules"})
def doctor(c, verbose=False, fix=False):
    """Run all dev_doctor rules to check code health."""
    print("🏥 Running XO Core Dev Doctor...")
    print(f"📁 Rules directory: {RULES_DIR}")
    
    if fix:
        print("🛠️ Auto-fix mode enabled - will attempt to fix failed rules")
    
    rules = load_rules()
    if not rules:
        print("⚠️ No rules found to check")
        return
    
    print(f"📋 Found {len(rules)} rule(s) to check")
    print("-" * 50)
    
    all_passed = True
    passed_count = 0
    failed_count = 0
    
    for filename, rule in rules:
        try:
            if apply_rule(filename, rule, fix=fix):
                passed_count += 1
                if verbose:
                    print(f"✅ {filename}: PASSED")
            else:
                failed_count += 1
                print(f"❌ {filename}: FAILED")
                all_passed = False
        except Exception as e:
            failed_count += 1
            print(f"❌ {filename}: ERROR - {e}")
            all_passed = False
        
        if verbose:
            print()
    
    print("-" * 50)
    print(f"📊 Results: {passed_count} passed, {failed_count} failed")
    
    if all_passed:
        print("🎉 All rules passed! Code health is good.")
    else:
        print("⚠️ Some rules failed. Please review and fix the issues above.")
        if fix:
            print("🛠️ Auto-fixes were attempted for failed rules.")
        return 1  # Exit with error code for CI/CD

@task
def list_rules(c):
    """List all available dev_doctor rules."""
    print("📋 Available Dev Doctor Rules:")
    print("-" * 40)
    
    rules = load_rules()
    if not rules:
        print("No rules found")
        return
    
    for filename, rule in rules:
        if 'id' in rule:
            # New format
            rule_name = rule.get('id', filename)
            rule_type = "new_format"
            description = rule.get('description', 'No description')
        else:
            # Old format
            rule_name = rule.get('name', filename)
            rule_type = rule.get('type', 'basic')
            description = rule.get('description', 'No description')
        
        print(f"📄 {filename}")
        print(f"   Name: {rule_name}")
        print(f"   Type: {rule_type}")
        print(f"   Description: {description}")
        print()

@task
def create_rule(c, name, type="file_exists", target_file=None, required_function=None, import_statement=None, description=""):
    """Create a new dev_doctor rule."""
    rule_data = {
        'name': name,
        'type': type,
        'description': description
    }
    
    if target_file:
        rule_data['target_file'] = target_file
    
    if required_function:
        rule_data['required_function'] = required_function
    
    if import_statement:
        rule_data['import_statement'] = import_statement
    
    # Create rules directory if it doesn't exist
    os.makedirs(RULES_DIR, exist_ok=True)
    
    # Generate filename
    filename = f"{name.lower().replace(' ', '_')}.yml"
    filepath = os.path.join(RULES_DIR, filename)
    
    with open(filepath, 'w') as f:
        yaml.dump(rule_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created rule: {filepath}")
    print(f"📄 Rule content:")
    print(yaml.dump(rule_data, default_flow_style=False, sort_keys=False))

ns = Collection("dev")
ns.add_task(fix_preview_import, name="fix-preview-import")
ns.add_task(check_packages, "check-packages")
ns.add_task(doctor, "doctor")
ns.add_task(list_rules, "list-rules")

# --- Guardrails task ---
@task
def guardrails(c):
    """Scan for task issues: missing docstrings, missing Collection declarations."""
    print("🧠 Dev Doctor Guardrails:")
    root = Path("src/xo_core/fab_tasks")
    task_count = 0
    issues = 0

    for py_file in root.rglob("*.py"):
        if "spec_sync" in py_file.name:
            continue
        content = py_file.read_text()
        try:
            tree = ast.parse(content)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    if not any(isinstance(dec, ast.Name) and dec.id == "task" for dec in node.decorator_list):
                        continue
                    task_count += 1
                    if not ast.get_docstring(node):
                        print(f"⚠️ Missing docstring in: {py_file} > {node.name}")
                        issues += 1
            if "ns = Collection(" not in content:
                print(f"⚠️ Missing Collection declaration in: {py_file}")
                issues += 1
        except Exception as e:
            print(f"❌ Failed to parse: {py_file} – {e}")
            issues += 1

    print(f"✅ Checked {task_count} @task definitions – {issues} issue(s) found.")

ns.add_task(guardrails, "guardrails")
ns.add_task(create_rule, "create-rule")

# Export the Fabric namespace
__all__ = ["ns"]