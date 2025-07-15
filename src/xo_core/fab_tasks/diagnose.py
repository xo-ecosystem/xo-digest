"""
Enhanced diagnostic tasks for xo-fab with advanced features.

Usage:
    xo-fab diagnose                    # Basic diagnostic
    xo-fab diagnose --export=report.md # Export to file
    xo-fab diagnose --pulse-bundle     # Generate pulse bundle
    xo-fab diagnose --upload=ipfs      # Upload to cloud
    xo-fab diagnose.ci                 # CI/CD workflow
    xo-fab diagnose.vault              # Vault-specific checks
    xo-fab diagnose.production         # Production environment check
    xo-fab diagnose.report             # Comprehensive report
"""

from invoke import task
from pathlib import Path
import os
import json
from datetime import datetime

# Add src to path for imports
from invoke import Collection
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from xo_core.fab_tasks.dynamic_loader import DynamicTaskLoader


@task
def diagnose(ctx, export=None, pulse_bundle=False, upload=None, 
            nft_storage_api_key=None, verbose=False, webhook_url=None,
            github_token=None, github_repo=None):
    """
    Run comprehensive diagnostic on the dynamic loader.
    
    Args:
        export: Path to export summary (supports .md, .json)
        pulse_bundle: Generate pulse bundle (index.mdx)
        upload: Upload to 'arweave' or 'ipfs'
        nft_storage_api_key: API key for nft.storage
        verbose: Enable verbose logging
        webhook_url: Webhook URL for notifications
        github_token: GitHub token for issue creation
        github_repo: GitHub repo (owner/repo) for issue creation
    """
    
    # Create loader with advanced features
    loader = DynamicTaskLoader(verbose=verbose, enable_advanced_features=True)
    
    # Load some test modules for demonstration
    test_configs = [
        loader.ModuleConfig("test_module1"),
        loader.ModuleConfig("test_module2"),
        loader.ModuleConfig("fail_module"),
        loader.ModuleConfig("no_tasks_module")
    ]
    
    for config in test_configs:
        loader.load_module(config, required=False)
    
    # Run diagnostic
    summary = loader.diagnose()
    
    # Export if requested
    exported_path = None
    if export:
        try:
            exported_path = loader.export_summary(export, pulse_bundle=pulse_bundle)
            print(f"\n📄 Summary exported to: {exported_path}")
        except Exception as e:
            print(f"\n❌ Failed to export summary: {e}")
    elif pulse_bundle:
        try:
            pulse_path = loader.export_pulse_bundle()
            print(f"\n📦 Pulse bundle exported to: {pulse_path}")
        except Exception as e:
            print(f"\n❌ Failed to export pulse bundle: {e}")
    
    # Upload if requested
    if upload and exported_path:
        try:
            upload_url = loader.upload_summary(exported_path, upload, nft_storage_api_key)
            print(f"\n☁️ Summary uploaded to: {upload_url}")
        except Exception as e:
            print(f"\n❌ Failed to upload summary: {e}")
    
    # Send webhook notification
    if webhook_url:
        try:
            success = loader.send_webhook_notification(webhook_url, summary)
            if success:
                print(f"\n🔔 Webhook notification sent")
            else:
                print(f"\n❌ Failed to send webhook notification")
        except Exception as e:
            print(f"\n❌ Webhook error: {e}")
    
    # Create GitHub issue for failures
    if github_token and github_repo and summary["total_failed"] > 0:
        try:
            repo_parts = github_repo.split("/")
            if len(repo_parts) == 2:
                owner, repo = repo_parts
                issue_url = loader.create_github_issue(owner, repo, github_token, summary)
                if issue_url:
                    print(f"\n🐙 GitHub issue created: {issue_url}")
                else:
                    print(f"\n❌ Failed to create GitHub issue")
        except Exception as e:
            print(f"\n❌ GitHub issue error: {e}")
    
    # Print summary
    print(f"\n📊 Diagnostic Summary:")
    print(f"  ✅ Loaded: {summary['total_loaded']}")
    print(f"  ❌ Failed: {summary['total_failed']}")
    print(f"  ⚠️ Skipped: {summary['total_skipped']}")
    print(f"  📊 Collections: {len(summary['collection_names'])}")
    
    return summary

@task
def ci(ctx, webhook_url=None, github_token=None, github_repo=None, 
       export_ci_report=True, verbose=False):
    """
    Run CI/CD workflow with notifications and reporting.
    
    Args:
        webhook_url: Webhook URL for notifications
        github_token: GitHub token for issue creation
        github_repo: GitHub repo (owner/repo) for issue creation
        export_ci_report: Export CI-friendly report
        verbose: Enable verbose logging
    """
    
    loader = DynamicTaskLoader(verbose=verbose, enable_advanced_features=True)
    
    print("🚀 Running CI/CD workflow...")
    
    # Run CI workflow
    summary = loader.run_ci_workflow(
        webhook_url=webhook_url,
        github_token=github_token,
        github_repo=github_repo
    )
    
    # Export CI report
    if export_ci_report:
        ci_path, exit_code = loader.export_ci_report()
        print(f"\n📋 CI report exported to: {ci_path}")
        print(f"Exit code: {exit_code}")
    
    # Print results
    print(f"\n📊 CI Workflow Results:")
    print(f"  ✅ Success: {summary.get('success', False)}")
    print(f"  📊 Loaded: {summary['total_loaded']}")
    print(f"  ❌ Failed: {summary['total_failed']}")
    print(f"  🐙 GitHub Issue: {summary.get('github_issue_url', 'None')}")
    
    if summary.get('exit_code', 0) != 0:
        print(f"\n❌ CI workflow failed with exit code: {summary.get('exit_code', 1)}")
        ctx.exit(summary.get('exit_code', 1))
    
    return summary

@task
def vault(ctx, vault_path=None, auto_fix=False, export=None, verbose=False):
    """
    Run Vault-specific diagnostic and auto-fix.
    
    Args:
        vault_path: Path to vault directory
        auto_fix: Attempt to auto-fix common issues
        export: Export vault report to file
        verbose: Enable verbose logging
    """
    
    loader = DynamicTaskLoader(verbose=verbose, enable_advanced_features=True)
    
    print("🔐 Running Vault diagnostic...")
    
    # Run vault workflow
    summary = loader.run_vault_workflow(
        vault_path=vault_path,
        auto_fix=auto_fix
    )
    
    # Print vault-specific results
    print(f"\n🔐 Vault Diagnostic Results:")
    print(f"  📁 Vault Path: {summary.get('vault_path', 'Not specified')}")
    print(f"  ❌ Issues Found: {len(summary.get('vault_issues', []))}")
    print(f"  🔧 Auto-fixes: {len(summary.get('auto_fixes', []))}")
    
    if summary.get('vault_issues'):
        print(f"\n❌ Vault Issues:")
        for issue in summary['vault_issues']:
            print(f"  - {issue}")
    
    if summary.get('auto_fixes'):
        print(f"\n🔧 Auto-fixes Applied:")
        for fix in summary['auto_fixes']:
            print(f"  - {fix}")
    
    # Export if requested
    if export:
        try:
            exported_path = loader.export_summary(export)
            print(f"\n📄 Vault report exported to: {exported_path}")
        except Exception as e:
            print(f"\n❌ Failed to export vault report: {e}")
    
    return summary

@task
def production(ctx, environment="production", export=None, verbose=False):
    """
    Run production environment checks.
    
    Args:
        environment: Environment name (production, staging, etc.)
        export: Export production report to file
        verbose: Enable verbose logging
    """
    
    loader = DynamicTaskLoader(verbose=verbose, enable_advanced_features=True)
    
    print(f"🏭 Running production checks for {environment}...")
    
    # Run production check
    summary = loader.run_production_check(environment=environment)
    
    # Print production results
    print(f"\n🏭 Production Check Results:")
    print(f"  🌍 Environment: {environment}")
    print(f"  ✅ Production Ready: {summary.get('production_ready', False)}")
    
    production_checks = summary.get('production_checks', {})
    
    # System resources
    sys_resources = production_checks.get('system_resources', {})
    print(f"  💻 System Resources: {'✅' if sys_resources.get('healthy', False) else '❌'}")
    
    # Security checks
    security = production_checks.get('security_checks', {})
    print(f"  🔒 Security: {'✅' if security.get('secure', False) else '❌'}")
    
    # Dependency health
    deps = production_checks.get('dependency_health', {})
    print(f"  📦 Dependencies: {'✅' if deps.get('healthy', False) else '❌'}")
    
    # Performance metrics
    perf = production_checks.get('performance_metrics', {})
    print(f"  ⚡ Performance: {'✅' if perf.get('acceptable_performance', False) else '❌'}")
    
    if not summary.get('production_ready', False):
        print(f"\n⚠️ Production readiness issues detected!")
        if sys_resources.get('recommendations'):
            print(f"  💻 System: {sys_resources['recommendations']}")
        if security.get('recommendations'):
            print(f"  🔒 Security: {security['recommendations']}")
        if deps.get('missing_dependencies'):
            print(f"  📦 Missing: {deps['missing_dependencies']}")
        if perf.get('recommendations'):
            print(f"  ⚡ Performance: {perf['recommendations']}")
    
    # Export if requested
    if export:
        try:
            exported_path = loader.export_summary(export)
            print(f"\n📄 Production report exported to: {exported_path}")
        except Exception as e:
            print(f"\n❌ Failed to export production report: {e}")
    
    return summary

@task
def report(ctx, path=None, upload=None, nft_storage_api_key=None, 
           include_real_world=True, include_ci_report=True, verbose=False):
    """
    Generate comprehensive diagnostic report with all features.
    
    Args:
        path: Path to export report (default: reports/loader_report.md)
        upload: Upload to 'arweave' or 'ipfs'
        nft_storage_api_key: API key for nft.storage
        include_real_world: Include real-world scenario tests
        include_ci_report: Include CI/CD report
        verbose: Enable verbose logging
    """
    
    loader = DynamicTaskLoader(verbose=verbose, enable_advanced_features=True)
    
    print("📋 Generating comprehensive diagnostic report...")
    
    # Run full diagnostic
    summary = loader.run_full_diagnostic(
        include_real_world=include_real_world,
        include_ci_report=include_ci_report
    )
    
    # Determine export path
    if path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"reports/loader_report_{timestamp}.md"
    
    # Ensure reports directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Export report
    try:
        exported_path = loader.export_summary(path)
        print(f"\n📄 Comprehensive report exported to: {exported_path}")
    except Exception as e:
        print(f"\n❌ Failed to export report: {e}")
        return summary
    
    # Upload if requested
    if upload:
        try:
            upload_url = loader.upload_summary(exported_path, upload, nft_storage_api_key)
            print(f"\n☁️ Report uploaded to: {upload_url}")
        except Exception as e:
            print(f"\n❌ Failed to upload report: {e}")
    
    # Print comprehensive summary
    print(f"\n📊 Comprehensive Report Summary:")
    print(f"  ✅ Loaded: {summary['total_loaded']}")
    print(f"  ❌ Failed: {summary['total_failed']}")
    print(f"  ⚠️ Skipped: {summary['total_skipped']}")
    print(f"  📊 Collections: {len(summary['collection_names'])}")
    
    if include_real_world:
        print(f"  🏭 Production Modules: {len(summary.get('production_modules', []))}")
        print(f"  🛠️ Development Modules: {len(summary.get('development_modules', []))}")
        print(f"  🔄 Circular Imports: {summary.get('circular_imports', 0)}")
        print(f"  📦 Missing Dependencies: {summary.get('missing_dependencies', 0)}")
    
    if include_ci_report:
        print(f"  📋 CI Report: {summary.get('ci_report_path', 'Not generated')}")
        print(f"  🚦 Exit Code: {summary.get('exit_code', 'N/A')}")
    
    return summary

@task
def real_world(ctx, verbose=False):
    """
    Run real-world scenario tests.
    
    Args:
        verbose: Enable verbose logging
    """
    
    loader = DynamicTaskLoader(verbose=verbose, enable_advanced_features=True)
    
    print("�� Running real-world scenario tests...")
    
    # Test production modules
    print("\n🏭 Testing production modules...")
    production_results = loader.load_production_modules()
    production_success = sum(1 for r in production_results if r.get('success', False))
    print(f"  ✅ Success: {production_success}/{len(production_results)}")
    
    # Test development modules
    print("\n🛠️ Testing development modules...")
    dev_results = loader.load_development_modules()
    dev_success = sum(1 for r in dev_results if r.get('success', False))
    print(f"  ✅ Success: {dev_success}/{len(dev_results)}")
    
    # Test circular imports
    print("\n🔄 Testing circular import handling...")
    circular_count = loader.simulate_circular_imports()
    print(f"  🔄 Circular imports detected: {circular_count}")
    
    # Test missing dependencies
    print("\n📦 Testing missing dependency handling...")
    missing_deps = loader.simulate_missing_dependencies()
    print(f"  📦 Missing dependencies detected: {missing_deps}")
    
    # Generate summary
    summary = {
        "production_modules": production_results,
        "development_modules": dev_results,
        "circular_imports": circular_count,
        "missing_dependencies": missing_deps,
        "total_tests": len(production_results) + len(dev_results) + 2,
        "successful_tests": production_success + dev_success + (0 if circular_count > 0 else 1) + (0 if missing_deps > 0 else 1)
    }
    
    print(f"\n📊 Real-world Test Summary:")
    print(f"  🧪 Total Tests: {summary['total_tests']}")
    print(f"  ✅ Successful: {summary['successful_tests']}")
    print(f"  ❌ Failed: {summary['total_tests'] - summary['successful_tests']}")
    
    return summary

@task
def webhook_test(ctx, webhook_url, service="slack", verbose=False):
    """
    Test webhook notifications.
    
    Args:
        webhook_url: Webhook URL to test
        service: Service type (slack, discord, generic)
        verbose: Enable verbose logging
    """
    
    loader = DynamicTaskLoader(verbose=verbose, enable_advanced_features=True)
    
    print(f"🔔 Testing webhook notification to {service}...")
    
    # Create test summary
    test_summary = {
        "total_loaded": 5,
        "total_failed": 2,
        "total_skipped": 1,
        "collection_names": ["test_collection"],
        "failed": ["test_fail_1", "test_fail_2"],
        "loaded": ["test_success_1", "test_success_2", "test_success_3"],
        "skipped": ["test_skip_1"]
    }
    
    # Send test notification
    try:
        success = loader.send_webhook_notification(webhook_url, test_summary, service)
        if success:
            print(f"✅ Webhook test successful!")
        else:
            print(f"❌ Webhook test failed")
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
    
    return {"success": success, "service": service, "webhook_url": webhook_url}

@task
def github_test(ctx, token, repo, verbose=False):
    """
    Test GitHub issue creation.
    
    Args:
        token: GitHub token
        repo: GitHub repository (owner/repo)
        verbose: Enable verbose logging
    """
    
    loader = DynamicTaskLoader(verbose=verbose, enable_advanced_features=True)
    
    print(f"🐙 Testing GitHub issue creation for {repo}...")
    
    # Create test summary with failures
    test_summary = {
        "total_loaded": 3,
        "total_failed": 2,
        "total_skipped": 0,
        "collection_names": ["test_collection"],
        "failed": ["test_fail_1", "test_fail_2"],
        "loaded": ["test_success_1"],
        "skipped": []
    }
    
    # Create test issue
    try:
        repo_parts = repo.split("/")
        if len(repo_parts) == 2:
            owner, repo_name = repo_parts
            issue_url = loader.create_github_issue(owner, repo_name, token, test_summary)
            if issue_url:
                print(f"✅ GitHub issue created: {issue_url}")
            else:
                print(f"❌ Failed to create GitHub issue")
        else:
            print(f"❌ Invalid repository format: {repo}")
    except Exception as e:
        print(f"❌ GitHub test error: {e}")
    
    return {"issue_url": issue_url if 'issue_url' in locals() else None, "repo": repo}

# Create namespace
ns = Collection("diagnose")
ns.add_task(diagnose)
ns.add_task(ci, name="ci")
ns.add_task(vault, name="vault")
ns.add_task(production, name="production")
ns.add_task(report, name="report")
ns.add_task(real_world, name="real_world")
ns.add_task(webhook_test, name="webhook_test")
ns.add_task(github_test, name="github_test") 