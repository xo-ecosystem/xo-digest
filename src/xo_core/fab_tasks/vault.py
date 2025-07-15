"""XO Vault Fabric tasks for secure content management and digest generation."""

from invoke import task, Collection
from pathlib import Path
import hashlib
import json
import rich
from datetime import datetime
import os


def get_pulse_files():
    """Get all pulse .mdx files from content/pulses/."""
    pulses_dir = Path("content/pulses")
    if not pulses_dir.exists():
        return []
    
    pulse_files = []
    for pulse_dir in pulses_dir.iterdir():
        if pulse_dir.is_dir():
            mdx_file = pulse_dir / "index.mdx"
            if mdx_file.exists():
                pulse_files.append(mdx_file)
    
    return pulse_files


def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def save_signed_data(mdx_path, content_hash, signed_path):
    """Save signed data to .signed file."""
    signed_data = {
        "mdx_file": str(mdx_path),
        "content_hash": content_hash,
        "signed_at": datetime.now().isoformat(),
        "signature_version": "1.0"
    }
    
    with open(signed_path, 'w') as f:
        json.dump(signed_data, f, indent=2)


@task
def sign_all(ctx):
    """
    🔏 Sign all pulse .mdx files under content/pulses/ and generate .signed files per pulse folder.
    
    Creates a .signed file for each pulse containing:
    - SHA256 hash of the .mdx content
    - Timestamp of signing
    - File path reference
    """
    rich.print("[bold blue]🔏 Signing all pulse files...[/bold blue]")
    
    pulse_files = get_pulse_files()
    if not pulse_files:
        rich.print("[yellow]⚠️  No pulse files found in content/pulses/[/yellow]")
        return
    
    signed_count = 0
    for mdx_path in pulse_files:
        try:
            # Calculate hash of the MDX content
            content_hash = calculate_file_hash(mdx_path)
            
            # Create .signed file in the same directory
            signed_path = mdx_path.parent / f"{mdx_path.stem}.signed"
            save_signed_data(mdx_path, content_hash, signed_path)
            
            rich.print(f"✅ Signed: {mdx_path.name} → {signed_path.name}")
            signed_count += 1
            
        except Exception as e:
            rich.print(f"[red]❌ Failed to sign {mdx_path}: {e}[/red]")
    
    rich.print(f"[green]🎉 Successfully signed {signed_count}/{len(pulse_files)} pulse files[/green]")


@task
def verify_all(ctx):
    """
    ✅ Verify that .signed files exist and match a SHA256 hash of their corresponding .mdx.
    
    Checks:
    - .signed files exist for each .mdx
    - Content hashes match current .mdx content
    - Signed data is valid JSON
    """
    rich.print("[bold blue]✅ Verifying all signed pulse files...[/bold blue]")
    
    pulse_files = get_pulse_files()
    if not pulse_files:
        rich.print("[yellow]⚠️  No pulse files found in content/pulses/[/yellow]")
        return
    
    verified_count = 0
    failed_count = 0
    
    for mdx_path in pulse_files:
        signed_path = mdx_path.parent / f"{mdx_path.stem}.signed"
        
        try:
            # Check if .signed file exists
            if not signed_path.exists():
                rich.print(f"[red]❌ Missing signature: {mdx_path.name}[/red]")
                failed_count += 1
                continue
            
            # Load signed data
            with open(signed_path, 'r') as f:
                signed_data = json.load(f)
            
            # Verify hash matches current content
            current_hash = calculate_file_hash(mdx_path)
            stored_hash = signed_data.get('content_hash')
            
            if current_hash == stored_hash:
                rich.print(f"✅ Verified: {mdx_path.name}")
                verified_count += 1
            else:
                rich.print(f"[red]❌ Hash mismatch: {mdx_path.name}[/red]")
                failed_count += 1
                
        except Exception as e:
            rich.print(f"[red]❌ Verification failed for {mdx_path.name}: {e}[/red]")
            failed_count += 1
    
    if failed_count == 0:
        rich.print(f"[green]🎉 All {verified_count} pulse files verified successfully![/green]")
    else:
        rich.print(f"[yellow]⚠️  {verified_count} verified, {failed_count} failed[/yellow]")


@task
def unlock_memetic_path(ctx):
    """
    🔓 Custom task that touches a .unlocked file in vault/memetic_path/, for lore-chain activation.
    
    Creates the memetic_path directory and .unlocked file to signal
    that the vault's memetic content is now accessible.
    """
    rich.print("[bold blue]🔓 Unlocking memetic path...[/bold blue]")
    
    memetic_dir = Path("vault/memetic_path")
    unlocked_file = memetic_dir / ".unlocked"
    
    try:
        # Create directory if it doesn't exist
        memetic_dir.mkdir(parents=True, exist_ok=True)
        
        # Touch the .unlocked file
        unlocked_file.touch()
        
        # Add some lore content
        lore_content = f"""# Memetic Path Unlocked

Unlocked at: {datetime.now().isoformat()}

The vault's memetic content is now accessible.
Lore-chain activation sequence complete.

🔓 Path: {unlocked_file.absolute()}
🧠 Status: Active
⚡ Power: Unlocked
"""
        
        with open(unlocked_file, 'w') as f:
            f.write(lore_content)
        
        rich.print(f"[green]✅ Memetic path unlocked: {unlocked_file}[/green]")
        rich.print("[cyan]🧠 Lore-chain activation sequence complete![/cyan]")
        
    except Exception as e:
        rich.print(f"[red]❌ Failed to unlock memetic path: {e}[/red]")


# Digest subcollection tasks
@task
def generate(ctx):
    """
    🧬 Generate daily digest markdown from pulses and store in vault/daily/YYYY-MM-DD.md.
    
    Creates a daily digest containing:
    - List of all pulses with their status
    - Summary of recent changes
    - Links to pulse content
    """
    rich.print("[bold blue]🧬 Generating daily digest...[/bold blue]")
    
    # Create vault/daily directory
    daily_dir = Path("vault/daily")
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename for today
    today = datetime.now().strftime("%Y-%m-%d")
    digest_file = daily_dir / f"{today}.md"
    
    try:
        # Get all pulse files
        pulse_files = get_pulse_files()
        
        # Generate digest content
        digest_content = f"""# XO Daily Digest - {today}

Generated at: {datetime.now().isoformat()}

## Pulse Summary

Total pulses: {len(pulse_files)}

"""
        
        # Add pulse details
        for mdx_path in pulse_files:
            pulse_name = mdx_path.parent.name
            signed_path = mdx_path.parent / f"{mdx_path.stem}.signed"
            
            # Get file stats
            mtime = datetime.fromtimestamp(mdx_path.stat().st_mtime)
            size = mdx_path.stat().st_size
            
            # Check if signed
            signed_status = "✅" if signed_path.exists() else "❌"
            
            digest_content += f"""### {pulse_name}
- **Status**: {signed_status} {'Signed' if signed_path.exists() else 'Unsigned'}
- **Last Modified**: {mtime.strftime('%Y-%m-%d %H:%M')}
- **Size**: {size:,} bytes
- **Path**: `{mdx_path}`

"""
        
        # Add footer
        digest_content += f"""
---
*Digest generated by XO Vault System*
*Date: {today}*
"""
        
        # Write digest file
        with open(digest_file, 'w') as f:
            f.write(digest_content)
        
        rich.print(f"[green]✅ Daily digest generated: {digest_file}[/green]")
        rich.print(f"[blue]📊 Summary: {len(pulse_files)} pulses documented[/blue]")
        
    except Exception as e:
        rich.print(f"[red]❌ Failed to generate digest: {e}[/red]")


@task
def push(ctx):
    """
    📤 Push latest digest files to public/ and optionally upload to IPFS/Arweave.
    
    Copies the most recent digest to public/digest/ and optionally
    uploads to decentralized storage if configured.
    """
    rich.print("[bold blue]📤 Pushing digest to public...[/bold blue]")
    
    daily_dir = Path("vault/daily")
    public_digest_dir = Path("public/digest")
    
    if not daily_dir.exists():
        rich.print("[yellow]⚠️  No daily digests found in vault/daily/[/yellow]")
        return
    
    try:
        # Create public digest directory
        public_digest_dir.mkdir(parents=True, exist_ok=True)
        
        # Find the most recent digest
        digest_files = list(daily_dir.glob("*.md"))
        if not digest_files:
            rich.print("[yellow]⚠️  No digest files found[/yellow]")
            return
        
        latest_digest = max(digest_files, key=lambda f: f.stat().st_mtime)
        
        # Copy to public
        public_digest = public_digest_dir / latest_digest.name
        with open(latest_digest, 'r') as src, open(public_digest, 'w') as dst:
            dst.write(src.read())
        
        rich.print(f"[green]✅ Digest pushed to: {public_digest}[/green]")
        
        # Optional: Upload to IPFS/Arweave (placeholder)
        try:
            # This would integrate with actual IPFS/Arweave libraries
            rich.print("[blue]🌐 IPFS/Arweave upload: Not configured[/blue]")
        except ImportError:
            rich.print("[yellow]⚠️  IPFS/Arweave libraries not available[/yellow]")
        
    except Exception as e:
        rich.print(f"[red]❌ Failed to push digest: {e}[/red]")


# Create subcollections
digest_ns = Collection("digest")
digest_ns.add_task(generate, name="generate")
digest_ns.add_task(push, name="push")

# Create main vault namespace
ns = Collection("vault")
ns.add_task(sign_all, name="sign-all")
ns.add_task(verify_all, name="verify-all")
ns.add_task(unlock_memetic_path, name="unlock-memetic-path")
ns.add_collection(digest_ns, name="digest")
