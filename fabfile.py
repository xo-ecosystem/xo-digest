from xo_core.fab_tasks.dev_doctor_tasks import ns as dev_doctor_ns
from xo_core.fab_tasks.pulse_tasks import ns as pulse_ns

# Patch preview import warning suppression
import logging
logging.getLogger().setLevel(logging.INFO)
from invoke import task, Collection
from pathlib import Path
from xo_core.fab_tasks.ipfs_tasks import ns as ipfs_ns
from xo_core.fab_tasks import pulse_tasks

# Add tasks to pulse namespace if they exist
try:
    pulse_ns.add_task(pulse_tasks.sign, "sign")
except AttributeError:
    pass  # Task already registered in the collection

try:
    pulse_ns.add_task(pulse_tasks.archive_all, "archive")
except AttributeError:
    pass  # Task already registered in the collection

try:
    pulse_ns.add_task(pulse_tasks.sync, "sync")
except AttributeError:
    pass  # Task already registered in the collection

@task
def push_logbook(c):
    """Simple logbook push task for testing."""
    print("📔 Push logbook task - simplified for testing")
    print("Use xo-fab ipfs.test-connection to test IPFS setup")

@task(help={"verbose": "Enable verbose output", "fix": "Attempt auto-fixes for failed rules"})
def doctor(c, verbose=False, fix=False):
    """Root-level doctor task that forwards to dev.doctor."""
    from xo_core.fab_tasks.dev_doctor_tasks import doctor as dev_doctor
    return dev_doctor(c, verbose=verbose, fix=fix)

# Create main namespace
ns = Collection()

# Add IPFS tasks
try:
    ns.add_collection(ipfs_ns, name="ipfs")
except Exception as e:
    import logging
    logging.warning(f"⚠️ IPFS namespace not loaded: {e}")

# Add dev_doctor tasks
try:
    ns.add_collection(dev_doctor_ns, name="dev")
except Exception as e:
    import logging
    logging.warning(f"⚠️ Dev doctor namespace not loaded: {e}")

# Add pulse tasks
try:
    ns.add_collection(pulse_ns, name="pulse")
except Exception as e:
    import logging
    logging.warning(f"⚠️ Pulse namespace not loaded: {e}")

# Add drop_patch tasks
try:
    from xo_core.fab_tasks.drop_patch import ns as drop_patch_ns
    ns.add_collection(drop_patch_ns, name="drop")
except ImportError as e:
    import logging
    logging.warning(f"⚠️ Drop patch namespace not loaded: {e}")

# Add preview tasks
try:
    from xo_core.fab_tasks.preview import ns as preview_ns
    ns.add_collection(preview_ns, name="preview")
except ImportError as e:
    import logging
    logging.warning(f"⚠️ Preview namespace not loaded: {e}")

# Add drop_meta_sync tasks
try:
    from xo_core.fab_tasks.drop_meta_sync import ns as drop_meta_sync_ns
    ns.add_collection(drop_meta_sync_ns, name="meta")
except ImportError as e:
    import logging
    logging.warning(f"⚠️ Drop meta sync namespace not loaded: {e}")

# Add sign_pulse tasks, if available
try:
    from xo_core.fab_tasks.vault.sign_pulse import ns as sign_pulse_ns
    ns.add_collection(sign_pulse_ns, name="sign_pulse")
except ImportError as e:
    import logging
    logging.warning(f"⚠️ Sign pulse namespace not loaded: {e}")

# Add sign_pulse_test tasks, if available
try:
    from xo_core.fab_tasks.vault.sign_pulse_test import ns as sign_pulse_test_ns
    ns.add_collection(sign_pulse_test_ns, name="sign_pulse_test")
except ImportError as e:
    import logging
    logging.warning(f"⚠️ Sign pulse test namespace not loaded: {e}")

# Add root-level doctor task
ns.add_task(doctor, "doctor")

@task(help={"ipfs": "Pin to IPFS", "arweave": "Upload to Arweave"})
def deploy_all(c, ipfs=False, arweave=False):
    """🚀 Deploy all major XO drop layers with optional pinning and logging."""
    print("🚀 XO Drop Deploy All - Full Vault Stack Integration")
    print("-" * 50)
    
    # Generate preview
    print("🔍 Generating preview...")
    c.run("xo-fab preview.generate --drop=eighth_seal_3d")
    
    # Deploy explorer (placeholder for now)
    print("🌐 Deploying explorer...")
    # c.run("xo-fab explorer.deploy")  # Uncomment when explorer.deploy exists
    
    # Optional IPFS pinning
    if ipfs:
        print("📌 Pinning to IPFS...")
        c.run("xo-fab ipfs.pin-file --path=public/vault/previews/eighth_seal_3d")
    
    # Optional Arweave upload
    if arweave:
        print("🌊 Uploading to Arweave...")
        c.run("xo-fab pulse.upload --path=public/vault/previews/eighth_seal_3d")
    
    # Log deployment
    log_path = Path("vault/logbook/deploy.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    with open(log_path, "a") as log_file:
        log_file.write(f"[{datetime.utcnow().isoformat()}] Deployed eighth_seal_3d\n")
    print(f"📝 Logged deployment to {log_path}")
    
    # Git tag and push
    c.run("git tag v0.1.0-eighth && git push origin v0.1.0-eighth")
    print("🏷️ Tagged and pushed: v0.1.0-eighth")
    
    # Integrate with Vault stack
    print("\n🔗 Integrating with Vault stack...")
    
    # Digest integration
    try:
        c.run("xo-fab digest.generate")
        print("  ✅ Digest updated")
    except:
        print("  ⚠️ Digest generation failed (continuing)")
    
    # Pulse integration
    try:
        c.run("xo-fab pulse.sync")
        print("  ✅ Pulse synced")
    except:
        print("  ⚠️ Pulse sync failed (continuing)")
    
    # Inbox integration
    try:
        c.run("xo-fab inbox.message --message='Deployed eighth_seal_3d drop'")
        print("  ✅ Inbox message sent")
    except:
        print("  ⚠️ Inbox message failed (continuing)")
    
    print("\n🎉 Full Vault stack deployment completed!")

# Add deploy_all to root namespace (avoiding conflict with drop.deploy)
ns.add_task(deploy_all, name="deploy-all")

# Define the default namespace
namespace = ns