# src/xo_core/fab_tasks/docs.py
from invoke import task, Collection
import os, time, jwt, requests
from pathlib import Path
from dotenv import set_key

# [o3-fix 2025-08-03] Removed unused import


@task
def token(c):
    """Fetch GitHub App Installation Token and export to .env.local"""
    app_id = os.getenv("XO_DOCS_APP_ID")
    installation_id = os.getenv("XO_DOCS_INSTALLATION_ID")
    pem_path = os.path.expanduser(os.getenv("XO_DOCS_PRIVATE_KEY_PATH"))

    if not app_id or not installation_id or not pem_path:
        raise EnvironmentError("❌ Missing XO_DOCS env variables")

    private_key = Path(pem_path).read_text()
    now = int(time.time())
    payload = {"iat": now, "exp": now + 600, "iss": int(app_id)}
    jwt_token = jwt.encode(payload, private_key, algorithm="RS256")

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    res = requests.post(url, headers=headers)

    if res.status_code != 201:
        raise RuntimeError(f"❌ Token fetch failed: {res.status_code} → {res.text}")

    token = res.json()["token"]
    print(f"✅ Token fetched → {token[:8]}...")

    # Export to .env.local for mkdocs deploy
    dotenv_path = Path(".env.local")
    dotenv_path.touch(exist_ok=True)
    set_key(dotenv_path, "GH_TOKEN", token)
    print(f"📦 Token written to .env.local as GH_TOKEN")


@task
def publish(c):
    """Deploy xo-core-docs to GitHub Pages using GitHub App token"""
    print("📚 Publishing documentation to GitHub Pages...")

    # Run deploy script
    result = c.run("python scripts/deploy_docs.py", warn=True)

    if result.ok:
        print("✅ Documentation published successfully!")
        print("📡 Available at: https://xo-ecosystem.github.io/xo-core-docs/")
    else:
        print("❌ Documentation publishing failed")
        print("💡 Tip: Run 'fab docs.token' first to refresh GitHub token")
        print("💡 Alternative: Use 'python scripts/deploy_docs.py' directly")


@task
def preview(c):
    """Launch local preview server for documentation development"""
    print("📚 Starting local documentation preview...")
    result = c.run("python scripts/docs_preview.py", warn=True)

    if result.ok:
        print("✅ Documentation preview completed")
    else:
        print("❌ Documentation preview failed")
        print("💡 Alternative: Use 'python scripts/docs_preview.py' directly")


ns = Collection("docs")
ns.add_task(token)
ns.add_task(publish)
ns.add_task(preview)
