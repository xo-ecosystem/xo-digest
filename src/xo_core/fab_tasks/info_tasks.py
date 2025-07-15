"""Information and documentation tasks for the dynamic task loader."""

from invoke import task
from typing import Dict, Any
import json
from pathlib import Path


@task
def namespace_info(ctx, verbose=False):
    """Show information about loaded task namespaces.
    
    Args:
        verbose: Show detailed information about each module
    """
    try:
        from xo_core.fab_tasks.dynamic_loader import load_all_modules, MODULE_CONFIGS
        from invoke import Collection
        
        # Create a temporary collection to get loading summary
        temp_ns = Collection()
        summary = load_all_modules(temp_ns, verbose=verbose)
        
        print("📊 Task Namespace Information")
        print("=" * 50)
        
        # Show loaded modules by category
        categories = {}
        for config in MODULE_CONFIGS:
            if config.path in summary['loaded_modules']:
                category = config.category
                if category not in categories:
                    categories[category] = []
                categories[category].append({
                    'name': config.alias or config.name,
                    'path': config.path,
                    'description': config.description,
                    'required': config.required
                })
        
        for category, modules in categories.items():
            print(f"\n🔹 {category.upper()} ({len(modules)} modules):")
            for module in modules:
                status = "✅" if module['required'] else "📦"
                print(f"  {status} {module['name']}")
                if verbose and module['description']:
                    print(f"     └─ {module['description']}")
        
        # Show failed modules
        if summary['failed_modules']:
            print(f"\n❌ Failed Modules ({len(summary['failed_modules'])}):")
            for failed in summary['failed_modules']:
                print(f"  - {failed}")
        
        # Show summary stats
        print(f"\n📈 Summary:")
        print(f"  Total loaded: {summary['total_loaded']}")
        print(f"  Total failed: {summary['total_failed']}")
        print(f"  Collection names: {', '.join(summary['collection_names'])}")
        
    except ImportError as e:
        print(f"❌ Error loading dynamic loader: {e}")


@task
def generate_docs(ctx, output="docs/task_namespaces.md"):
    """Generate documentation for all task namespaces.
    
    Args:
        output: Output file path for the documentation
    """
    try:
        from xo_core.fab_tasks.dynamic_loader import MODULE_CONFIGS
        from invoke import Collection
        
        # Create a temporary collection to get loading summary
        temp_ns = Collection()
        from xo_core.fab_tasks.dynamic_loader import load_all_modules
        summary = load_all_modules(temp_ns, verbose=False)
        
        # Generate markdown documentation
        doc_content = []
        doc_content.append("# Task Namespaces Documentation")
        doc_content.append("")
        doc_content.append("This document provides an overview of all available task namespaces in the XO Core project.")
        doc_content.append("")
        
        # Group modules by category
        categories = {}
        for config in MODULE_CONFIGS:
            category = config.category
            if category not in categories:
                categories[category] = []
            categories[category].append(config)
        
        # Generate category sections
        for category, configs in categories.items():
            doc_content.append(f"## {category.title()} Tasks")
            doc_content.append("")
            
            for config in configs:
                status = "✅" if config.required else "📦"
                doc_content.append(f"### {status} {config.alias or config.name}")
                doc_content.append("")
                doc_content.append(f"**Module:** `{config.path}`")
                doc_content.append("")
                
                if config.description:
                    doc_content.append(f"**Description:** {config.description}")
                    doc_content.append("")
                
                if config.path in summary['loaded_modules']:
                    doc_content.append("**Status:** Loaded")
                else:
                    doc_content.append("**Status:** Not available")
                doc_content.append("")
        
        # Add usage section
        doc_content.append("## Usage")
        doc_content.append("")
        doc_content.append("To see all available tasks:")
        doc_content.append("```bash")
        doc_content.append("fab --list")
        doc_content.append("```")
        doc_content.append("")
        doc_content.append("To get detailed namespace information:")
        doc_content.append("```bash")
        doc_content.append("fab namespace.info")
        doc_content.append("```")
        doc_content.append("")
        
        # Write to file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(doc_content))
        
        print(f"✅ Generated documentation: {output_path}")
        print(f"📊 Documented {len(MODULE_CONFIGS)} task modules across {len(categories)} categories")
        
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")


@task
def validate_modules(ctx):
    """Validate that all required modules can be imported and have expected structure."""
    try:
        from xo_core.fab_tasks.dynamic_loader import MODULE_CONFIGS, DynamicTaskLoader
        
        loader = DynamicTaskLoader(verbose=True)
        print("🔍 Validating task modules...")
        print("=" * 50)
        
        validation_results = {
            'valid': [],
            'invalid': [],
            'missing': []
        }
        
        for config in MODULE_CONFIGS:
            print(f"\nChecking: {config.path}")
            
            try:
                # Try to import
                mod = __import__(config.path, fromlist=["*"])
                
                # Validate structure
                if loader._validate_module(mod, config):
                    validation_results['valid'].append(config.path)
                    print(f"  ✅ Valid")
                else:
                    validation_results['invalid'].append(config.path)
                    print(f"  ❌ Invalid structure")
                    
            except ImportError:
                if config.required:
                    validation_results['missing'].append(config.path)
                    print(f"  ❌ Missing (required)")
                else:
                    print(f"  ⚠️  Missing (optional)")
        
        # Summary
        print(f"\n📊 Validation Summary:")
        print(f"  Valid: {len(validation_results['valid'])}")
        print(f"  Invalid: {len(validation_results['invalid'])}")
        print(f"  Missing (required): {len(validation_results['missing'])}")
        
        if validation_results['missing']:
            print(f"\n❌ Missing required modules:")
            for missing in validation_results['missing']:
                print(f"  - {missing}")
        
        if validation_results['invalid']:
            print(f"\n⚠️  Invalid modules:")
            for invalid in validation_results['invalid']:
                print(f"  - {invalid}")
        
        return len(validation_results['missing']) == 0 and len(validation_results['invalid']) == 0
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False


@task
def list_categories(ctx):
    """List all available task categories."""
    try:
        from xo_core.fab_tasks.dynamic_loader import MODULE_CONFIGS
        
        categories = {}
        for config in MODULE_CONFIGS:
            category = config.category
            if category not in categories:
                categories[category] = []
            categories[category].append(config.alias or config.name)
        
        print("📂 Available Task Categories:")
        print("=" * 40)
        
        for category, modules in categories.items():
            print(f"\n🔹 {category.title()} ({len(modules)} modules):")
            for module in modules:
                print(f"  - {module}")
        
        print(f"\n📊 Total: {len(categories)} categories, {len(MODULE_CONFIGS)} modules")
        
    except Exception as e:
        print(f"❌ Error listing categories: {e}") 

from invoke import Collection

ns = Collection("info")
ns.add_task(namespace_info, name="info")
ns.add_task(generate_docs, name="generate-docs")
ns.add_task(validate_modules, name="validate-modules")
ns.add_task(list_categories, name="list-categories")

__all__ = ["ns"]