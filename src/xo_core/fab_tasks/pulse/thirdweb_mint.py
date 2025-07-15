from invoke import task
from xo_core.fab_tasks.pulse.utils import test_pulse_data
import requests
import os

@task(help={"pulse_path": "Path to the pulse .md or .signed file"})
def thirdweb_mint(c, pulse_path="content/pulses/pulse.xoseals.com.md"):
    """
    🪙 Mint a Pulse NFT on Thirdweb
    """
    pulse = test_pulse_data(pulse_path)
    title = pulse.get("title", "Untitled Pulse")
    slug = pulse.get("slug", "untitled")

    print(f"🔗 Preparing to mint '{title}' with slug: {slug}")

    token = os.getenv("THIRDWEB_API_TOKEN")
    if not token:
        print("❌ THIRDWEB_API_TOKEN not set in environment.")
        return

    payload = {
        "name": title,
        "description": pulse.get("excerpt", "Pulse excerpt."),
        "image": pulse.get("image", "https://xoseals.com/default.png"),
        "external_url": f"https://xoseals.com/pulse/{slug}"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "https://api.thirdweb.com/v1/mint"  # Update this URL if needed

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Minted successfully: {result}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Minting failed: {e}")


@task(help={"signed_path": "Path to the signed .md file (optional)"})
def post_sign_mint(c, signed_path=None):
    """
    🪙 Run the post-sign mint hook manually or auto-detect the latest signed file
    """
    if not signed_path:
        import glob
        signed_files = sorted(glob.glob("content/pulses/*.signed"), reverse=True)
        if not signed_files:
            print("❌ No signed pulse files found.")
            return
        signed_path = signed_files[0]
        print(f"🪙 Auto-selected latest signed pulse: {signed_path}")
    post_sign_hook(c, signed_path)

# Post-sign hook to mint after signing
def post_sign_hook(c, signed_path):
    print(f"🪙 Post-sign hook triggered for: {signed_path}")
    thirdweb_mint(c, pulse_path=signed_path)


from invoke import Collection
ns = Collection("pulse")
ns.add_task(thirdweb_mint, name="thirdweb_mint")
ns.add_task(post_sign_mint, name="post_sign_mint")