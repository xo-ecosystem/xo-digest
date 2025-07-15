from invoke import task, Collection
from datetime import datetime

@task(help={})
def auto(c):
    """Automate the full XO Vault chain: sign-all, pin-all, verify-all."""
    start_time = datetime.now()
    print(f"🚀 Starting XO Vault chain at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Sign all pulses and coins
    print("\n📝 Step 1: Signing all pulses and coins...")
    c.run("xo-fab vault-tasks.sign-all", pty=True)
    
    # Step 2: Pin all signed content (including TXID files)
    print("\n📦 Step 2: Pinning all signed content to IPFS and Arweave...")
    c.run("xo-fab vault-pin-task.pin-all --include-txid", pty=True)
    
    # Step 3: Verify all
    print("\n✅ Step 3: Verifying all content...")
    c.run("xo-fab vault-cleaned.verify-all", pty=True)
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n🎉 XO Vault chain completed in {duration.total_seconds():.1f} seconds")
    print(f"📊 Check pin manifest: vault/.pins/pin_manifest.json")
    print(f"📋 Check pin logs: vault/.pins/pin_log_{datetime.now().strftime('%Y-%m-%d')}.txt")

# Create a local namespace for this module only
chain_ns = Collection("chain")
chain_ns.add_task(auto, name="auto")

# Export the namespace for external use
ns = chain_ns 