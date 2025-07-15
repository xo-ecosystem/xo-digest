from xo_core.utils.pulse_loader import load_all_pulses

@task
def sign_all(c):
    from xo_core.vault.sign_pulse import sign_pulse
    from xo_core.vault.ipfs_utils import log_status
    from xo_core.vault.preview_generator import render_signed_preview
    
    print("🔏 Signing all vault entries...")

    pulses = load_all_pulses()
    if not pulses:
        log_status("⚠️ No pulses found to sign.")
        return

    for pulse in pulses:
    result = sign_pulse(pulse)
    log_status(f"✅ Pulse signed and pinned: {result.get('ipfs_hash')}")
    
    # 🎨 Render preview file
    pulse["ipfs_hash"] = result.get("ipfs_hash")
    render_signed_preview(
        pulse,
        output_path=f"vault/preview/{pulse['slug']}.html"
    )

ns = Collection("sign")
ns.add_task(sign_all, name="all")
