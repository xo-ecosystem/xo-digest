from invoke import Collection, task
from pathlib import Path
import yaml
import json
import sys
import os

ns = Collection("agent")


@task
def dispatch(c, prompt_path=None, persona=None, task_name=None, drop_id=None, goals=None):
    """
    Dispatch an agent task based on .agent-prompt.yml or direct parameters.
    
    Usage:
    xo-fab agent.dispatch:"drops/message_bottle/.agent-prompt.yml"
    xo-fab agent.dispatch --persona=vault_keeper --task="publish drop" --drop_id=message_bottle
    """
    
    # Load prompt from file if provided
    if prompt_path:
        prompt_file = Path(prompt_path)
        if not prompt_file.exists():
            print(f"❌ Prompt file not found: {prompt_file}")
            return False
            
        try:
            with open(prompt_file, 'r') as f:
                prompt_data = yaml.safe_load(f)
            
            persona = prompt_data.get('persona', persona)
            task_name = prompt_data.get('task', task_name)
            drop_id = prompt_data.get('drop_id', drop_id)
            goals = prompt_data.get('goals', goals)
            description = prompt_data.get('description', '')
            
            print(f"🤖 Agent Dispatch: {persona}")
            print(f"📋 Task: {task_name}")
            print(f"🎯 Drop: {drop_id}")
            print(f"📝 Description: {description}")
            print(f"🎯 Goals: {goals}")
            
        except yaml.YAMLError as e:
            print(f"❌ Error reading prompt file: {e}")
            return False
    
    # Validate required parameters
    if not all([persona, task_name, drop_id]):
        print("❌ Missing required parameters: persona, task, drop_id")
        print("Usage: xo-fab agent.dispatch --persona=vault_keeper --task='publish drop' --drop_id=message_bottle")
        return False
    
    print(f"\n🚀 Executing {persona} task: {task_name}")
    print(f"📦 Target drop: {drop_id}")
    
    # Execute based on persona and task
    if persona == "vault_keeper":
        if task_name == "publish drop":
            return execute_vault_publish(c, drop_id, goals)
        elif task_name == "audit drop":
            return execute_drop_audit(c, drop_id, goals)
        else:
            print(f"❌ Unknown task for vault_keeper: {task_name}")
            return False
    else:
        print(f"❌ Unknown persona: {persona}")
        return False


def execute_vault_publish(c, drop_id, goals):
    """Execute vault publish task"""
    print(f"\n🔧 Executing vault publish for {drop_id}")
    
    # First audit the drop
    print("🔍 Pre-publish audit...")
    audit_result = execute_drop_audit(c, drop_id, goals)
    
    if not audit_result:
        print("❌ Drop audit failed - aborting publish")
        return False
    
    # Execute vault publish
    print("\n⬆️ Publishing to vault...")
    try:
        from .vault import vault_publish
        result = vault_publish(c, drop_id)
        return result
    except Exception as e:
        print(f"❌ Vault publish failed: {e}")
        return False


def execute_drop_audit(c, drop_id, goals):
    """Execute drop audit task"""
    print(f"\n🔍 Executing drop audit for {drop_id}")
    
    try:
        from .vault import drop_audit
        result = drop_audit(c, drop_id)
        return result
    except Exception as e:
        print(f"❌ Drop audit failed: {e}")
        return False


@task
def discover(c, drops_dir="drops"):
    """
    Discover all .agent-prompt.yml files in drops directory.
    Usage: xo-fab agent.discover
    """
    drops_path = Path(drops_dir)
    if not drops_path.exists():
        print(f"❌ Drops directory not found: {drops_path}")
        return
    
    print(f"🔍 Discovering agent prompts in {drops_path}")
    
    prompt_files = list(drops_path.rglob(".agent-prompt.yml"))
    
    if not prompt_files:
        print("ℹ️ No .agent-prompt.yml files found")
        return
    
    print(f"📋 Found {len(prompt_files)} agent prompts:")
    
    for prompt_file in prompt_files:
        try:
            with open(prompt_file, 'r') as f:
                prompt_data = yaml.safe_load(f)
            
            persona = prompt_data.get('persona', 'unknown')
            task = prompt_data.get('task', 'unknown')
            drop_id = prompt_data.get('drop_id', 'unknown')
            
            relative_path = prompt_file.relative_to(drops_path)
            drop_dir = relative_path.parent
            
            print(f"  📁 {drop_dir}")
            print(f"     🤖 {persona} | {task} | {drop_id}")
            print(f"     🚀 xo-fab agent.dispatch:\"{prompt_file}\"")
            print()
            
        except yaml.YAMLError as e:
            print(f"  ❌ Error reading {prompt_file}: {e}")


@task
def generate_prompt(c, drop_id, persona="vault_keeper", task="publish drop"):
    """
    Generate a .agent-prompt.yml file for a drop.
    Usage: xo-fab agent.generate-prompt:"message_bottle"
    """
    drop_path = Path("drops") / drop_id
    
    if not drop_path.exists():
        print(f"❌ Drop directory not found: {drop_path}")
        return False
    
    prompt_file = drop_path / ".agent-prompt.yml"
    
    # Default goals based on task
    if task == "publish drop":
        goals = [
            "Upload all files to IPFS if needed",
            "Patch .traits.yml with CID references", 
            "Patch drop.status.json if required",
            "Output deployment log or summary to /vault/logbook/"
        ]
        description = f"Validate and publish the drop `{drop_id}`. Ensure all images are uploaded to IPFS, .traits.yml is present and patched, and status.json includes updated CID references. Finalize the Vault bundle."
    elif task == "audit drop":
        goals = [
            "Check all required files are present",
            "Validate JSON/YAML syntax",
            "Check for IPFS placeholders",
            "Report readiness status"
        ]
        description = f"Audit the drop `{drop_id}` for completeness and readiness. Check all required files, validate syntax, and identify any missing components."
    else:
        goals = ["Complete the specified task"]
        description = f"Execute {task} for drop {drop_id}"
    
    prompt_data = {
        "persona": persona,
        "task": task,
        "drop_id": drop_id,
        "description": description,
        "goals": goals
    }
    
    try:
        with open(prompt_file, 'w') as f:
            yaml.dump(prompt_data, f, sort_keys=False, default_flow_style=False)
        
        print(f"✅ Generated agent prompt: {prompt_file}")
        print(f"🤖 Persona: {persona}")
        print(f"📋 Task: {task}")
        print(f"🎯 Drop: {drop_id}")
        print(f"🚀 Dispatch: xo-fab agent.dispatch:\"{prompt_file}\"")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating prompt: {e}")
        return False


# Add tasks to namespace
ns.add_task(dispatch)
ns.add_task(discover)
ns.add_task(generate_prompt) 