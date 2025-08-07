# [o3-fix 2025-08-03] Vault tasks updated for lazy community import
from invoke import Collection, task

def get_community_tasks():
    """Lazy import to avoid circular dependencies"""
    from xo_core.vault import get_community_tasks as _get_community_tasks
    return _get_community_tasks()

# [o3-fix 2025-08-03] removed premature ns linking; root namespace declared later


@task
def bundle(c, name):
    print(f"📦 Bundling vault package: {name}")
    c.run(f"mkdir -p vault/bundles/{name}")
    c.run(f"cp -r vault/daily/{name} vault/bundles/{name}")
    print(f"✅ Vault bundle created at vault/bundles/{name}")


@task
def archive(c, name):
    print(f"🗃 Archiving vault package: {name}")
    c.run(f"mkdir -p vault/archive/")
    c.run(f"cp -r vault/bundles/{name} vault/archive/")
    print(f"📦 Bundle {name} archived to vault/archive/")


@task
def sign_all(c):
    print("🧾 Signing all .coin.yml and .mdx files in vault/")
    # Insert logic here


@task
def explorer_deploy(c):
    print("🚀 Deploying vault explorer")
    # Insert logic here


@task
def digest_export(c):
    """Copy digest output to public viewer directory."""
    c.run("mkdir -p webapp/digest/vault/daily")
    c.run("cp -r vault/daily/* webapp/digest/vault/daily/")
    print("📤 Digest exported to webapp/digest/vault/daily/")


# Community tasks
@task(
    help={
        "slug": "Pulse slug to render",
        "output_dir": "Output directory for HTML files",
    }
)
def inbox_render(c, slug=None, output_dir="vault/daily"):
    """Render inbox comments to HTML."""
    get_community_tasks().inbox_render(c, slug, output_dir)


@task(help={"slug": "Pulse slug to analyze", "create_pulse": "Create reply pulse"})
def agent_reply_suggest(c, slug=None, create_pulse=False):
    """Analyze inbox and suggest replies."""
    get_community_tasks().agent_reply_suggest(c, slug, create_pulse)


@task(
    help={
        "slug": "Pulse slug",
        "channels": "Comma-separated channels",
        "filters": "Comma-separated filters",
        "health_check": "Broadcast health check",
    }
)
def signal_broadcast(c, slug=None, channels="inbox", filters=None, health_check=False):
    """Broadcast social signals."""
    get_community_tasks().signal_broadcast(c, slug, channels, filters, health_check)


@task(help={"slug": "Pulse slug", "all_features": "Activate all features"})
def community_activate(c, slug=None, all_features=False):
    """Activate all community features for a slug."""
    get_community_tasks().community_activate(c, slug, all_features)


@task
def community_status(c):
    """Show community system status."""
    get_community_tasks().community_status(c)


@task
def digest_index(c):
    """Generate index.json for vault/daily digest viewer."""
    import json, os

    entries = []
    for root, dirs, files in os.walk("vault/daily"):
        for file in files:
            if file.endswith(".mdx"):
                slug = file.replace(".mdx", "")
                entries.append({"slug": slug, "title": slug.replace("_", " ").title()})
    with open("vault/daily/index.json", "w") as f:
        json.dump(entries, f, indent=2)
    print(f"📦 index.json generated with {len(entries)} entries.")


@task
def unseal(c):
    """Unseal vault using keys from various sources."""
    from vault.unseal import vault_unseal

    success = vault_unseal()
    if success:
        print("✅ Vault unseal task completed successfully")
    else:
        print("❌ Vault unseal task failed")
        exit(1)


@task
def status(c):
    """Check vault status and health."""
    from xo_core.vault.utils import vault_status

    print("🔍 Checking vault status...")
    is_unsealed = vault_status()
    if is_unsealed:
        print("✅ Vault is healthy and unsealed")
    else:
        print("❌ Vault is sealed or unhealthy")


@task
def pull_secrets(c):
    """Pull vault secrets from GitHub or local encrypted file."""
    from xo_core.vault.utils import vault_pull_secrets

    print("📥 Pulling vault secrets...")
    vault_pull_secrets()


@task
def zip_bundle(c):
    """Create a ZIP bundle of vault contents for backup/transfer."""
    from xo_core.vault.utils import zip_vault_bundle

    print("📦 Creating vault bundle...")
    bundle_path = zip_vault_bundle()
    if bundle_path:
        print(f"✅ Bundle created: {bundle_path}")
    else:
        print("❌ Failed to create bundle")


@task
def status_log(c):
    """Sync current vault state into logbook."""
    from vault.bootstrap import write_vault_bootstrap_log

    print("📓 Writing vault status to logbook...")
    write_vault_bootstrap_log()
    print("✅ Vault status logged")


@task
def sign_advanced(c, content_type="pulse", algorithm="ed25519"):
    """Sign all content of a specific type with advanced cryptographic signing."""
    from src.xo_core.vault.signing import XOVaultSigner
    from datetime import datetime

    print(f"🔐 Signing all {content_type} content with {algorithm}...")

    try:
        signer = XOVaultSigner(algorithm=algorithm)
        key_name = f"{content_type}-signing-key-{datetime.now().strftime('%Y%m')}"

        # Ensure key exists
        try:
            signer.generate_key_pair(key_name, algorithm)
            print(f"✅ Generated signing key: {key_name}")
        except:
            print(f"✅ Using existing signing key: {key_name}")

        # List available keys
        keys = signer.list_keys()
        print(f"📋 Available keys: {len(keys)}")

        print(f"✅ {content_type} signing setup complete")

    except Exception as e:
        print(f"❌ Signing setup failed: {e}")
        exit(1)


@task
def verify_all(c, signed_file=None):
    """Verify all signed content."""
    from src.xo_core.vault.signing import verify_signed_content
    from pathlib import Path
    import json

    print("🔍 Verifying signed content...")

    try:
        if signed_file:
            # Verify specific file
            with open(signed_file, "r") as f:
                signed_document = json.load(f)

            result = verify_signed_content(signed_document)
            if result["valid"]:
                print(f"✅ Signature valid: {signed_file}")
            else:
                print(f"❌ Signature invalid: {signed_file}")
        else:
            # Verify all signed content in vault directory
            vault_dir = Path("vault")
            signed_files = list(vault_dir.rglob("*.signed.json"))

            valid_count = 0
            total_count = len(signed_files)

            for signed_file in signed_files:
                try:
                    with open(signed_file, "r") as f:
                        signed_document = json.load(f)

                    result = verify_signed_content(signed_document)
                    if result["valid"]:
                        valid_count += 1
                        print(f"✅ {signed_file.name}")
                    else:
                        print(f"❌ {signed_file.name}")
                except Exception as e:
                    print(f"⚠️ {signed_file.name}: {e}")

            print(
                f"\n📊 Verification Summary: {valid_count}/{total_count} valid signatures"
            )

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        exit(1)


@task
def rotate_keys(c, key_pattern=None):
    """Rotate signing keys."""
    from src.xo_core.vault.signing import XOVaultSigner

    print("🔄 Rotating signing keys...")

    try:
        signer = XOVaultSigner()
        keys = signer.list_keys()

        rotated_count = 0
        for key in keys:
            key_name = key["name"]

            # Apply pattern filter if specified
            if key_pattern and key_pattern not in key_name:
                continue

            try:
                result = signer.rotate_key(key_name)
                print(f"✅ Rotated key: {key_name}")
                rotated_count += 1
            except Exception as e:
                print(f"⚠️ Failed to rotate {key_name}: {e}")

        print(f"✅ Key rotation complete: {rotated_count} keys rotated")

    except Exception as e:
        print(f"❌ Key rotation failed: {e}")
        exit(1)


# Create namespace
ns = Collection("vault")

# Add local tasks
ns.add_task(sign_all, name="sign-all")
ns.add_task(explorer_deploy, name="explorer-deploy")
ns.add_task(digest_export, name="digest-export")
ns.add_task(digest_index, name="digest-index")
ns.add_task(bundle)
ns.add_task(archive)

# Add core vault tasks
ns.add_task(unseal)
ns.add_task(status)
ns.add_task(pull_secrets, name="pull-secrets")
ns.add_task(zip_bundle, name="zip-bundle")
ns.add_task(status_log, name="status-log")

# Add advanced signing tasks
ns.add_task(sign_advanced, name="sign-advanced")
ns.add_task(verify_all, name="verify-all")
ns.add_task(rotate_keys, name="rotate-keys")

# Add community tasks
ns.add_task(inbox_render, name="inbox-render")
ns.add_task(agent_reply_suggest, name="agent-reply-suggest")
ns.add_task(signal_broadcast, name="signal-broadcast")
ns.add_task(community_activate, name="community-activate")
ns.add_task(community_status, name="community-status")

# Import and add external modules
try:
    from .vault_sign import ns as vault_sign_ns

    ns.add_collection(vault_sign_ns, name="sign")
except ImportError as e:
    print(f"⚠️ Could not import vault_sign: {e}")

try:
    from .vault_explorer_preview import ns as explorer_ns

    ns.add_collection(explorer_ns, name="explorer")
except ImportError as e:
    print(f"⚠️ Could not import vault_explorer_preview: {e}")

try:
    from .vault_pulse_sync import ns as pulse_sync_ns

    ns.add_collection(pulse_sync_ns, name="pulse")
except ImportError as e:
    print(f"⚠️ Could not import vault_pulse_sync: {e}")
