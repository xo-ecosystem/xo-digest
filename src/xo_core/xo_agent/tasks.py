import json
import os
from pathlib import Path

import requests
import yaml
from invoke import Collection, task


@task
def deploy_persona(c):
    """Deploy a persona."""
    print("🧬 Deploying persona...")


@task
def reload_all(c):
    """Reload all personas."""
    print("🔄 Reloading all agent personas...")
    # Insert logic here


@task
def list_personas(c):
    base = Path("vault/personas")  # or use `vault/seeds` if that's the actual path
    if not base.exists():
        print("⚠️  No persona directory found.")
        return
    for f in sorted(base.glob("*.yml")):
        print(f"👤 {f.name}")


@task
def test_dialog(c, persona="default"):
    print(f"🧪 Simulating dialog for: {persona}")
    # This would be a stub for calling agent0/test endpoint or LLM test


@task
def seed_personas_from_vault(c):
    vault_dir = Path("vault/personas")
    if not vault_dir.exists():
        alt_dir = Path("vault/seeds")
        if alt_dir.exists():
            print("🔁 Using fallback: vault/seeds/")
            vault_dir = alt_dir
        else:
            print("📁 Creating vault/personas...")
            vault_dir.mkdir(parents=True, exist_ok=True)

    # Add sample if empty
    if not any(vault_dir.glob("*.yml")):
        example = {
            "name": "example_persona",
            "description": "This is a sample persona.",
            "traits": ["friendly", "helpful"],
            "prompt": "You are a helpful assistant.",
        }
        example_path = vault_dir / "example_persona.yml"
        with open(example_path, "w") as f:
            yaml.dump(example, f)
        print(f"📝 Sample persona created at: {example_path}")

    # Check endpoint availability
    try:
        r = requests.get("http://localhost:8002/health", timeout=3)
        if r.status_code != 200:
            print("❌ agent0 API not healthy. Aborting.")
            return
    except Exception as e:
        print(f"❌ agent0 not reachable: {e}")
        return

    headers = {}
    token = os.environ.get("AGENT0_API_KEY")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    status_map = {}

    for yml_file in sorted(vault_dir.glob("*.yml")):
        print(f"📦 Seeding from: {yml_file.name}")
        with open(yml_file) as f:
            data = yaml.safe_load(f)

        try:
            response = requests.post(
                "http://localhost:8002/personas", json=data, headers=headers, timeout=5
            )
            name = data.get("name", yml_file.stem)
            if response.status_code == 200:
                print(f"✅ Deployed: {name}")
                status_map[name] = {"status": "success"}

                # Trigger webhook
                try:
                    webhook_response = requests.post(
                        "http://localhost:8002/sign", json={"slug": name}, timeout=3
                    )
                    if webhook_response.status_code == 200:
                        print(f"🔗 Webhook triggered for: {name}")
                    else:
                        print(
                            f"⚠️ Webhook failed for: {name} → {webhook_response.status_code}"
                        )
                except Exception as we:
                    print(f"❌ Webhook error for {name}: {we}")
            else:
                print(f"⚠️ Failed: {name} → {response.status_code}")
                status_map[name] = {"status": "error", "code": response.status_code}
        except Exception as e:
            print(f"❌ Error deploying {yml_file.name}: {e}")
            status_map[yml_file.stem] = {"status": "error", "exception": str(e)}

    with open("vault/persona_status.json", "w") as f:
        json.dump(status_map, f, indent=2)
        print("📝 Status log saved to vault/persona_status.json")


# Generate MDX from persona YAMLs
@task
def generate_mdx(c):
    source_dir = Path("vault/personas")
    target_dir = source_dir / "mdx"
    target_dir.mkdir(parents=True, exist_ok=True)

    for yml_file in sorted(source_dir.glob("*.yml")):
        with open(yml_file) as f:
            data = yaml.safe_load(f)

        name = data.get("name", yml_file.stem)
        mdx_path = target_dir / f"{name}.mdx"

        content = f"""---
title: "{name}"
description: "{data.get('description', '')}"
traits: {data.get('traits', [])}
---

# {name}

{data.get('prompt', 'No prompt provided.')}
"""

        with open(mdx_path, "w") as out:
            out.write(content)

        print(f"📝 Generated: {mdx_path}")


ns = Collection("xo_agent")
ns.add_task(deploy_persona, name="deploy-persona")
ns.add_task(reload_all, name="reload-all")  # ✅ no wrapping
ns.add_task(list_personas, name="list-personas")
ns.add_task(test_dialog, name="test-dialog")
ns.add_task(seed_personas_from_vault, name="seed-personas-from-vault")
ns.add_task(generate_mdx, name="generate-mdx")

namespace = ns
