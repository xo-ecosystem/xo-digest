import json
import os
from pathlib import Path
from datetime import datetime
from invoke import task, Collection

@task(help={"slug": "Show details for specific pulse slug", "format": "Output format: text, json, or html"})
def view_pulse(c, slug=None, format="text"):
    """
    👁️ Enhanced pulse viewer with pin status, dates, and links
    """
    patterns = [
        "content/pulses/**/*.mdx",
        "vault/.signed/**/*.signed",
        "vault/.txid/**/*.txid",
    ]
    
    found_files = set()
    for pat in patterns:
        found_files.update(Path(".").glob(pat))
    
    if slug:
        found_files = {f for f in found_files if slug in str(f)}
    
    if not found_files:
        print("⚠️ No pulses found.")
        return
    
    pulses_data = []
    
    for file_path in sorted(found_files):
        pulse_slug = file_path.stem
        print(f"\n🔍 Analyzing: {pulse_slug}")
        
        pulse_info = {
            "slug": pulse_slug,
            "file": str(file_path),
            "type": file_path.suffix[1:],  # Remove the dot
            "pin_status": "❌ Not pinned",
            "signed_date": None,
            "pinned_date": None,
            "ipfs_link": None,
            "arweave_link": None,
            "gateway_link": None
        }
        
        # Check for signed date
        signed_file = Path(f"vault/.signed/{pulse_slug}.signed")
        if signed_file.exists():
            try:
                with open(signed_file, 'r') as f:
                    signed_data = json.load(f)
                    if 'timestamp' in signed_data:
                        pulse_info["signed_date"] = signed_data['timestamp']
                        print(f"  📅 Signed: {signed_data['timestamp']}")
            except:
                pass
        
        # Check for pin metadata
        pin_meta_file = file_path.with_suffix(file_path.suffix + ".pin_meta")
        if pin_meta_file.exists():
            try:
                with open(pin_meta_file, 'r') as f:
                    pin_meta = json.load(f)
                
                # Handle both old and new pin metadata formats
                cid = pin_meta.get('cid') or pin_meta.get('ipfs_cid')
                pinned_at = pin_meta.get('pinned_at')
                gateway = pin_meta.get('gateway') or pin_meta.get('ipfs_gateway')
                arweave_txid = pin_meta.get('arweave_txid')
                
                if cid and pinned_at:
                    pulse_info["pin_status"] = "✅ Pinned"
                    pulse_info["pinned_date"] = pinned_at
                    pulse_info["ipfs_link"] = f"ipfs://{cid}"
                    pulse_info["gateway_link"] = gateway
                    
                    print(f"  📌 Pin Status: ✅ Pinned")
                    print(f"  📅 Pinned: {pinned_at}")
                    print(f"  🔗 IPFS: ipfs://{cid}")
                    if gateway:
                        print(f"  🌐 Gateway: {gateway}")
                    
                    # Show Arweave TXID if available
                    if arweave_txid:
                        pulse_info["arweave_link"] = f"https://arweave.net/{arweave_txid}"
                        print(f"  🔗 Arweave: https://arweave.net/{arweave_txid}")
                else:
                    pulse_info["pin_status"] = "⚠️ Incomplete pin data"
                    print(f"  📌 Pin Status: ⚠️ Incomplete pin data")
            except Exception as e:
                pulse_info["pin_status"] = "❌ Pin metadata error"
                print(f"  📌 Pin Status: ❌ Pin metadata error: {e}")
        else:
            print(f"  📌 Pin Status: ❌ Not pinned")
        
        # Check for Arweave transaction (legacy .txid files)
        txid_file = Path(f"vault/.txid/{pulse_slug}.txid")
        if txid_file.exists():
            try:
                with open(txid_file, 'r') as f:
                    txid = f.read().strip()
                    # Only set arweave_link if not already set by pin metadata
                    if not pulse_info["arweave_link"]:
                        pulse_info["arweave_link"] = f"https://arweave.net/{txid}"
                        print(f"  🔗 Arweave (legacy): https://arweave.net/{txid}")
            except:
                pass
        
        pulses_data.append(pulse_info)
    
    # Output in requested format
    if format == "json":
        print(json.dumps(pulses_data, indent=2))
    elif format == "html":
        print(generate_html_view(pulses_data))
    else:  # text format
        print_summary(pulses_data)


def print_summary(pulses_data):
    """Print a summary table of all pulses"""
    print(f"\n📊 Pulse Summary ({len(pulses_data)} pulses):")
    print("-" * 80)
    print(f"{'Slug':<20} {'Type':<8} {'Pin':<8} {'Signed':<12} {'Pinned':<12}")
    print("-" * 80)
    
    for pulse in pulses_data:
        signed_date = pulse["signed_date"][:10] if pulse["signed_date"] else "N/A"
        pinned_date = pulse["pinned_date"][:10] if pulse["pinned_date"] else "N/A"
        pin_icon = "✅" if "✅" in pulse["pin_status"] else "❌"
        
        print(f"{pulse['slug']:<20} {pulse['type']:<8} {pin_icon:<8} {signed_date:<12} {pinned_date:<12}")


def generate_html_view(pulses_data):
    """Generate HTML view of pulses with status badges and links"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>XO Pulse Viewer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .pulse { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; }
            .status { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
            .pinned { background: #d4edda; color: #155724; }
            .unpinned { background: #f8d7da; color: #721c24; }
            .link { color: #007bff; text-decoration: none; }
            .link:hover { text-decoration: underline; }
            .date { color: #6c757d; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>XO Pulse Viewer</h1>
    """
    
    for pulse in pulses_data:
        status_class = "pinned" if "✅" in pulse["pin_status"] else "unpinned"
        html += f"""
        <div class="pulse">
            <h3>{pulse['slug']} <span class="status {status_class}">{pulse['pin_status']}</span></h3>
            <p><strong>Type:</strong> {pulse['type']}</p>
        """
        
        if pulse["signed_date"]:
            html += f'<p class="date"><strong>Signed:</strong> {pulse["signed_date"]}</p>'
        
        if pulse["pinned_date"]:
            html += f'<p class="date"><strong>Pinned:</strong> {pulse["pinned_date"]}</p>'
        
        if pulse["ipfs_link"]:
            html += f'<p><strong>IPFS:</strong> <a href="{pulse["gateway_link"]}" class="link" target="_blank">{pulse["ipfs_link"]}</a></p>'
        
        if pulse["arweave_link"]:
            html += f'<p><strong>Arweave:</strong> <a href="{pulse["arweave_link"]}" class="link" target="_blank">{pulse["arweave_link"]}</a></p>'
        
        html += "</div>"
    
    html += """
    </body>
    </html>
    """
    
    return html


@task(help={"slug": "Generate viewer for specific pulse"})
def export_html(c, slug=None):
    """
    📄 Export pulse viewer as HTML file
    """
    html_content = generate_html_view([])  # Will be populated by view_pulse
    
    # Get pulses data
    patterns = [
        "content/pulses/**/*.mdx",
        "vault/.signed/**/*.signed",
        "vault/.txid/**/*.txid",
    ]
    
    found_files = set()
    for pat in patterns:
        found_files.update(Path(".").glob(pat))
    
    if slug:
        found_files = {f for f in found_files if slug in str(f)}
    
    pulses_data = []
    for file_path in sorted(found_files):
        # Simplified data collection for HTML export
        pulse_slug = file_path.stem
        pulse_info = {
            "slug": pulse_slug,
            "type": file_path.suffix[1:],
            "pin_status": "❌ Not pinned",
            "signed_date": None,
            "pinned_date": None,
            "ipfs_link": None,
            "arweave_link": None,
            "gateway_link": None
        }
        
        # Add pin metadata if available
        pin_meta_file = file_path.with_suffix(file_path.suffix + ".pin_meta")
        if pin_meta_file.exists():
            try:
                with open(pin_meta_file, 'r') as f:
                    pin_meta = json.load(f)
                cid = pin_meta.get('cid')
                pinned_at = pin_meta.get('pinned_at')
                gateway = pin_meta.get('gateway')
                
                if cid and pinned_at:
                    pulse_info["pin_status"] = "✅ Pinned"
                    pulse_info["pinned_date"] = pinned_at
                    pulse_info["ipfs_link"] = f"ipfs://{cid}"
                    pulse_info["gateway_link"] = gateway
            except:
                pass
        
        pulses_data.append(pulse_info)
    
    html_content = generate_html_view(pulses_data)
    
    output_file = f"pulse_viewer_{slug or 'all'}.html"
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"📄 HTML viewer exported to: {output_file}")


ns = Collection("pulse-viewer")
ns.add_task(view_pulse, name="view")
ns.add_task(export_html, name="export-html") 