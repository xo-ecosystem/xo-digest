from invoke import task, Collection
from pathlib import Path

# Import preview functions directly
from xo_core.fab_tasks.preview import generate, validate, list_drops, deploy

@task(help={"drop": "Name of the drop bundle", "open": "Open the preview folder after generation"})
def preview_generate(c, drop="eighth_seal_3d", open=False):
    """🔍 Generate preview files for a specific drop."""
    return generate(c, drop=drop, open=open)

@task(help={"drop": "Name of the drop bundle"})
def preview_validate(c, drop="eighth_seal_3d"):
    """🔍 Validate preview files for a specific drop."""
    return validate(c, drop=drop)

@task
def preview_list(c):
    """📋 List available drops for preview generation."""
    return list_drops(c)

@task(help={"drop": "Name of the drop bundle"})
def preview_deploy(c, drop="eighth_seal_3d"):
    """🚀 Deploy preview to public directory and log deployment."""
    return deploy(c, drop=drop)

@task(help={"ipfs": "Pin to IPFS", "arweave": "Upload to Arweave"})
def deploy_all(c, ipfs=False, arweave=False):
    """🚀 Deploy all major XO drop layers with optional pinning and logging."""
    print("🚀 XO Drop Deploy All - Full Vault Stack Integration")
    print("-" * 50)
    
    # Generate preview
    print("🔍 Generating preview...")
    preview_generate(c, drop="eighth_seal_3d")
    
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

# Create namespace
ns = Collection()
ns.add_task(preview_generate, name="preview.generate")
ns.add_task(preview_validate, name="preview.validate")
ns.add_task(preview_list, name="preview.list")
ns.add_task(preview_deploy, name="preview.deploy")
ns.add_task(deploy_all, name="deploy-all")

# Define the default namespace
namespace = ns 