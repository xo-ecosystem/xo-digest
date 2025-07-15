# XO Core Dev Doctor

A code health monitoring system for XO Core that ensures code quality, consistency, and proper wiring of components.

## 🏥 What is Dev Doctor?

Dev Doctor is a Fabric task-based system that runs automated checks against your codebase to ensure:

- Required functions exist in expected files
- Proper imports are in place
- Files exist where they should
- Code follows established patterns
- Vault components are properly wired

## 🚀 Quick Start

### Run all checks:
```bash
invoke dev.doctor
```

### Run with verbose output:
```bash
invoke dev.doctor --verbose
```

### List all available rules:
```bash
invoke dev.list-rules
```

### Create a new rule:
```bash
invoke dev.create-rule "My Rule Name" --type="required_function" --target-file="src/path/file.py" --required-function="my_function"
```

## 📋 Rule Types

### 1. `required_function`
Checks if a specific function exists in a target file.

```yaml
name: Ensure pulse.sign is wired
type: required_function
target_file: src/xo_core/vault/sign_pulse.py
required_function: sign_pulse
description: Ensure the sign_pulse function is defined for Vault pulse signing
```

### 2. `required_import`
Checks if a specific import statement exists in a target file.

```yaml
name: Ensure IPFS utils are imported
type: required_import
target_file: src/xo_core/vault/ipfs_utils.py
import_statement: "from xo_core.vault.ipfs_utils import pin_to_ipfs"
description: Ensure the pin_to_ipfs function is properly imported
```

### 3. `file_exists`
Checks if a specific file exists.

```yaml
name: Ensure sign_pulse.py file exists
type: file_exists
target_file: src/xo_core/vault/sign_pulse.py
description: Ensure the sign_pulse.py file exists in the vault directory
```

## 🛠️ Creating Rules

### Manual Creation
Create a `.yml` file in `dev_doctor/rules/` with the following structure:

```yaml
name: Your Rule Name
type: required_function  # or required_import, file_exists
target_file: path/to/target/file.py
required_function: function_name  # for required_function type
import_statement: "import statement"  # for required_import type
description: Description of what this rule checks

# Optional: Codex hints for AI assistance
codex_hints:
  - "cursor: codex: Check that 'function_name' is defined"
  - "cursor: codex.fixme: If missing, create the function"

# Optional: Related files
related_files:
  - path/to/related/file1.py
  - path/to/related/file2.py

# Optional: Auto-fix configuration
auto_fix:
  enabled: true
  template: |
    def your_function():
        # Auto-generated template
        pass
```

### Using the CLI
```bash
# Create a required_function rule
invoke dev.create-rule "Check My Function" \
  --type="required_function" \
  --target-file="src/my_module.py" \
  --required-function="my_function" \
  --description="Ensure my_function exists"

# Create a required_import rule
invoke dev.create-rule "Check Import" \
  --type="required_import" \
  --target-file="src/my_module.py" \
  --import-statement="from my_package import my_function" \
  --description="Ensure my_function is imported"
```

## 🔧 Integration

### GitHub Actions
The system includes a GitHub Action workflow (`.github/workflows/dev-doctor.yml`) that runs on:
- Push to main/develop branches
- Pull requests to main/develop branches

### Pre-commit Hooks
Use the pre-commit hook script (`dev_doctor/pre-commit-hook.py`) to run checks before commits:

```bash
# Make the hook executable
chmod +x dev_doctor/pre-commit-hook.py

# Add to your pre-commit configuration
```

### CI/CD Integration
Add to your CI pipeline:
```yaml
- name: Run Dev Doctor
  run: invoke dev.doctor
```

## 🧠 Codex Integration

Dev Doctor rules can include Codex hints for AI assistance:

```yaml
codex_hints:
  - "cursor: codex: Check that 'sign_pulse' is defined in 'sign_pulse.py'"
  - "cursor: codex.fixme: If sign_pulse function is missing, create it with proper signature"
```

These hints help AI assistants understand what to check and how to fix issues.

## 📁 File Structure

```
dev_doctor/
├── README.md                 # This file
├── pre-commit-hook.py       # Pre-commit hook script
└── rules/                   # Rule definitions
    ├── sign_pulse.yml       # Example: check sign_pulse function
    ├── ipfs_utils_import.yml # Example: check IPFS imports
    └── sign_pulse_file.yml  # Example: check file exists
```

## 🎯 Best Practices

1. **Be Specific**: Make rules target specific files and functions
2. **Add Descriptions**: Always include clear descriptions
3. **Use Codex Hints**: Help AI assistants understand the rules
4. **Test Rules**: Verify rules work before committing
5. **Keep Rules Focused**: One rule per concern
6. **Document Dependencies**: Use `related_files` to show connections

## 🔍 Troubleshooting

### Rule not being picked up
- Ensure the file ends with `.yml` or `.yaml`
- Check YAML syntax is valid
- Verify the file is in `dev_doctor/rules/`

### Function not found
- Check the function name spelling
- Verify the target file path is correct
- Ensure the function definition pattern matches

### Import not found
- Check the exact import statement
- Verify whitespace and quotes match
- Ensure the target file exists

## 🤝 Contributing

When adding new rules:

1. Create the rule file in `dev_doctor/rules/`
2. Test with `invoke dev.doctor`
3. Add to this README if it's a new rule type
4. Consider adding Codex hints for AI assistance

## 📊 Example Output

```
🏥 Running XO Core Dev Doctor...
📁 Rules directory: /path/to/dev_doctor/rules
📋 Found 3 rule(s) to check
--------------------------------------------------
🔍 Checking rule: Ensure pulse.sign is wired
✅ Function 'sign_pulse' found in src/xo_core/vault/sign_pulse.py
🔍 Checking rule: Ensure IPFS utils are imported
✅ Import statement found: from xo_core.vault.ipfs_utils import pin_to_ipfs
🔍 Checking rule: Ensure sign_pulse.py file exists
✅ File exists: src/xo_core/vault/sign_pulse.py
--------------------------------------------------
📊 Results: 3 passed, 0 failed
🎉 All rules passed! Code health is good.
``` 