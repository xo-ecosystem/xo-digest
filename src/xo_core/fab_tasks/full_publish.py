from invoke import task
from datetime import datetime
import json
from pathlib import Path

@task
def full_publish(c, slug="test_pulse", dry_run=False):
    """
    🚀 Full publish chain: create pulse → sign → sync → archive → pin → verify
    """
    start_time = datetime.now()
    print(f"📡 Launching full publish for: {slug}")
    print(f"⏰ Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Create new pulse
    print(f"\n🆕 Step 1: Creating new pulse '{slug}'...")
    c.run(f"xo-fab pulse.new --slug {slug}", warn=True)
    
    # Step 2: Sign the pulse
    print(f"\n✍️ Step 2: Signing pulse '{slug}'...")
    c.run(f"xo-fab pulse.sign --slug {slug}", warn=True)
    
    # Step 3: Sync the pulse
    print(f"\n🔄 Step 3: Syncing pulse '{slug}'...")
    c.run(f"xo-fab pulse.sync --slug {slug}", warn=True)
    
    # Step 4: Archive the pulse
    print(f"\n📦 Step 4: Archiving pulse '{slug}'...")
    c.run(f"xo-fab pulse.archive --slug {slug} {'--dry-run' if dry_run else ''}", warn=True)
    
    # Step 5: Run full vault chain (includes pinning and verification)
    print(f"\n🔗 Step 5: Running full vault chain (sign → pin → verify)...")
    c.run("xo-fab vault.auto.auto", warn=True)
    
    # Step 6: Display comprehensive summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n" + "="*60)
    print(f"✅ Full publish flow completed!")
    print(f"⏱️ Total duration: {duration.total_seconds():.1f} seconds")
    print(f"📅 Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show pin manifest summary if available
    manifest_path = Path("vault/.pins/pin_manifest.json")
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            txid_count = len(manifest)
            if txid_count > 0:
                print(f"\n📊 Pin Manifest Summary:")
                print(f"  🔗 Total TXID entries: {txid_count}")
                
                # Show recent entries
                recent_entries = list(manifest.items())[-3:]  # Last 3 entries
                for txid_key, entry in recent_entries:
                    ipfs_cid = entry.get('ipfs_cid', 'N/A')
                    arweave_tx = entry.get('arweave_tx', 'N/A')
                    print(f"  📄 {entry.get('file', txid_key)}:")
                    print(f"    🔗 IPFS: {ipfs_cid}")
                    print(f"    🌐 Arweave: {arweave_tx}")
        except Exception as e:
            print(f"⚠️ Could not read pin manifest: {e}")
    
    # Show log file location
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = Path(f"vault/.pins/pin_log_{today}.txt")
    if log_path.exists():
        print(f"\n📋 Detailed logs: {log_path}")
    
    print(f"\n🎉 Full publish flow completed successfully!")

from invoke import Collection
ns = Collection("full")
ns.add_task(full_publish, name="publish") 