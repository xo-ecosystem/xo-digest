"""
Environment Management Tasks
Git-aware .envrc switching and environment management
"""

import os
import subprocess
from pathlib import Path
from invoke import task, Collection

@task(help={"mode": "Environment mode: xo, fab2, link", "apply": "Apply changes and run direnv allow"})
def switch(c, mode="xo", apply=False):
    """Switch .envrc.link to different environment configurations"""
    print(f"🔄 Switching environment mode to: {mode}")
    
    # Define target files
    targets = {
        "xo": ".envrc",
        "fab2": ".envrc.fab2", 
        "link": ".envrc.link"
    }
    
    if mode not in targets:
        print(f"❌ Invalid mode: {mode}. Valid modes: {', '.join(targets.keys())}")
        return False
    
    target = targets[mode]
    
    # Check if target exists
    if not Path(target).exists():
        print(f"❌ Target file {target} does not exist")
        return False
    
    # Clean up broken symlinks
    cleanup_broken_links()
    
    # Create symlink
    try:
        link_path = Path(".envrc.link")
        if link_path.exists():
            link_path.unlink()
        link_path.symlink_to(target)
        print(f"✅ Linked .envrc.link → {target}")
    except OSError as e:
        if e.errno == 17:  # File exists error
            # Force remove and recreate
            link_path.unlink(missing_ok=True)
            link_path.symlink_to(target)
            print(f"✅ Forced link .envrc.link → {target}")
        else:
            print(f"❌ Failed to create symlink: {e}")
            return False
    except Exception as e:
        print(f"❌ Failed to create symlink: {e}")
        return False
    
    # Apply changes if requested
    if apply:
        return apply_envrc(c)
    
    return True

@task
def relink(c):
    """Recreate .envrc.link if broken or stale"""
    print("🔗 Relinking .envrc.link...")
    
    # Check if .envrc.link exists and is valid
    link_path = Path(".envrc.link")
    if link_path.exists() and link_path.is_symlink():
        try:
            target = link_path.resolve()
            if target.exists():
                print(f"✅ .envrc.link is valid: {link_path} → {target}")
                return True
        except:
            pass
    
    # Try to relink to default
    if Path(".envrc").exists():
        return switch(c, mode="xo", apply=False)
    elif Path(".envrc.fab2").exists():
        return switch(c, mode="fab2", apply=False)
    else:
        print("❌ No valid .envrc files found for relinking")
        return False

@task(help={"apply": "Apply changes and run direnv allow"})
def git_switch(c, apply=False):
    """Git-aware .envrc switching based on current branch/tag"""
    print("🌿 Git-aware environment switching...")
    
    # Get current Git branch
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True
        )
        branch = result.stdout.strip()
        print(f"📍 Current branch: {branch}")
    except subprocess.CalledProcessError:
        print("❌ Not in a Git repository")
        return False
    except FileNotFoundError:
        print("❌ Git not found in PATH")
        return False
    
    # Determine target based on branch patterns
    target_mode = determine_git_target(branch)
    
    if target_mode:
        print(f"🎯 Switching to {target_mode} mode for branch '{branch}'")
        return switch(c, mode=target_mode, apply=apply)
    else:
        print(f"⚠️  Unknown branch pattern: {branch}")
        print("💡 Consider adding a pattern or using .envrc.link.default")
        return False

@task
def status(c):
    """Show current .envrc.link status and Git context"""
    print("📊 Environment Status")
    print("-" * 40)
    
    # Check .envrc.link
    link_path = Path(".envrc.link")
    if link_path.exists() and link_path.is_symlink():
        try:
            target = link_path.resolve()
            print(f"🔗 .envrc.link → {target.name}")
            if target.exists():
                print("✅ Link is valid")
            else:
                print("❌ Target file missing")
        except:
            print("❌ Broken symlink")
    else:
        print("❌ .envrc.link not found")
    
    # Check .envrc
    envrc_path = Path(".envrc")
    if envrc_path.exists():
        if envrc_path.is_symlink():
            try:
                target = envrc_path.resolve()
                print(f"🔗 .envrc → {target.name}")
            except:
                print("❌ .envrc is broken symlink")
        else:
            print("📄 .envrc is regular file")
    else:
        print("❌ .envrc not found")
    
    # Git context
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True
        )
        branch = result.stdout.strip()
        print(f"🌿 Git branch: {branch}")
        
        target_mode = determine_git_target(branch)
        if target_mode:
            print(f"🎯 Git-aware target: {target_mode}")
        else:
            print("⚠️  No Git pattern match")
    except:
        print("🌿 Git context: Not available")

@task(help={"config": "Path to .xo.envrc.json config file"})
def git_watch(c, config=".xo.envrc.json"):
    """Watch for Git changes and auto-switch environments"""
    print("👀 Git watch mode - monitoring for branch changes...")
    
    # Load configuration
    config_data = load_git_config(config)
    
    # Get initial branch
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True
        )
        current_branch = result.stdout.strip()
        print(f"📍 Starting on branch: {current_branch}")
    except:
        print("❌ Failed to get current branch")
        return False
    
    # Monitor for changes (simplified - in real implementation would use file watching)
    print("💡 Git watch would monitor for branch changes and auto-switch")
    print("💡 Use 'git checkout <branch>' to test switching")
    
    return True

def cleanup_broken_links():
    """Clean up broken symlinks"""
    for link_name in [".envrc.link", ".envrc"]:
        link_path = Path(link_name)
        if link_path.exists() and link_path.is_symlink():
            try:
                target = link_path.resolve()
                if not target.exists():
                    print(f"🧹 Cleaning broken symlink: {link_name}")
                    link_path.unlink()
            except:
                print(f"🧹 Cleaning broken symlink: {link_name}")
                link_path.unlink()

def apply_envrc(c):
    """Apply .envrc changes and run direnv allow"""
    try:
        # Create .envrc symlink if it doesn't exist
        if not Path(".envrc").exists():
            Path(".envrc").symlink_to(".envrc.link")
            print("✅ Created .envrc → .envrc.link")
        
        # Run direnv allow
        result = subprocess.run(["direnv", "allow"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ direnv allow completed")
            return True
        else:
            print(f"⚠️  direnv allow failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠️  direnv not found - skipping direnv allow")
        return True
    except Exception as e:
        print(f"❌ Failed to apply .envrc: {e}")
        return False

def determine_git_target(branch):
    """Determine target environment based on Git branch patterns"""
    # Modern XO patterns
    modern_patterns = ["main", "master", "xo", "dev/xo", "feature/xo"]
    if branch in modern_patterns or branch.startswith("xo/"):
        return "xo"
    
    # Legacy patterns
    legacy_patterns = ["legacy", "fab2", "stable", "v1", "v2"]
    if branch in legacy_patterns or branch.startswith("legacy/"):
        return "fab2"
    
    # Check for .envrc.link.default fallback
    if Path(".envrc.link.default").exists():
        return "link"
    
    return None

def load_git_config(config_path):
    """Load Git-aware environment configuration"""
    import json
    
    if Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Default configuration
    return {
        "patterns": {
            "modern": ["main", "master", "xo", "dev/xo", "feature/xo"],
            "legacy": ["legacy", "fab2", "stable", "v1", "v2"]
        },
        "targets": {
            "modern": ".envrc",
            "legacy": ".envrc.fab2",
            "fallback": ".envrc.link.default"
        }
    }

# Create environment namespace
env_ns = Collection("env")
env_ns.add_task(switch, name="switch")
env_ns.add_task(relink, name="relink")
env_ns.add_task(git_switch, name="git-switch")
env_ns.add_task(status, name="status")
env_ns.add_task(git_watch, name="git-watch")