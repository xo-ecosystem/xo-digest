import datetime
import sys

from fastapi import FastAPI, Request
from pydantic import BaseModel


def log(msg, color="reset"):
    colors = {
        "green": "\033[92m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "reset": "\033[0m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
    }
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    color_code = colors.get(color, colors["reset"])
    print(f"{color_code}[{timestamp}] {msg}{colors['reset']}", file=sys.stdout)


class SlugRequest(BaseModel):
    slug: str


app = FastAPI()


@app.post("/sign")
def sign_persona(data: SlugRequest):
    log(f"✍️ Signing requested for: {data.slug}", "blue")
    # Append to signed log
    import json
    from pathlib import Path

    import requests

    signed_log = Path("vault/personas/.signed.json")
    signed_data = {}
    if signed_log.exists():
        with open(signed_log) as f:
            signed_data = json.load(f)

    signed_data[data.slug] = {"status": "signed"}

    with open(signed_log, "w") as f:
        json.dump(signed_data, f, indent=2)
    log(f"📝 Signed log updated: {signed_log}", "green")

    # Auto-publish logic placeholder
    try:
        log(f"🚀 Auto-publishing persona: {data.slug}", "cyan")
        # Simulate call to explorer or external system
        # requests.post("http://localhost:8003/publish", json={"slug": data.slug}, timeout=3)
    except Exception as pub_err:
        log(f"⚠️ Auto-publish failed for {data.slug}: {pub_err}", "yellow")

    # Trigger explorer deployment
    try:
        from urllib.parse import quote

        encoded_slug = quote(data.slug)
        explorer_res = requests.post(
            f"http://localhost:8004/explorer/deploy?slug={encoded_slug}", timeout=5
        )
        if explorer_res.status_code == 200:
            log(f"📡 Explorer deployed for: {data.slug}", "yellow")
            # Save to deployed log
            deployed_log = Path("vault/personas/.deployed.json")
            deployed_data = {}
            if deployed_log.exists():
                with open(deployed_log) as f:
                    deployed_data = json.load(f)
            deployed_data[data.slug] = {"status": "deployed"}
            with open(deployed_log, "w") as f:
                json.dump(deployed_data, f, indent=2)
            log(f"📝 Deployed log updated: {deployed_log}", "green")
        else:
            log(f"⚠️ Explorer deploy failed → {explorer_res.status_code}", "yellow")
    except Exception as e:
        log(f"❌ Explorer call error: {e}", "red")

    # Retry logic for IPFS/Arweave publishing
    for attempt in range(3):
        try:
            publish_payload = {"slug": data.slug}
            publish_res = requests.post(
                "http://localhost:8005/vault/publish", json=publish_payload, timeout=5
            )
            if publish_res.status_code == 200:
                log(f"📦 Published to IPFS/Arweave: {data.slug}", "green")
                break
            else:
                log(
                    f"⚠️ Attempt {attempt+1}: IPFS/Arweave failed → {publish_res.status_code}",
                    "yellow",
                )
        except Exception as e:
            log(f"❌ Attempt {attempt+1} IPFS/Arweave error: {e}", "red")

    # Real Discord/Inbox webhook
    try:
        webhook_url = "http://localhost:8006/notify"
        webhook_payload = {"slug": data.slug, "event": "persona-signed"}
        webhook_res = requests.post(webhook_url, json=webhook_payload, timeout=3)
        if webhook_res.status_code == 200:
            log(f"🔔 Discord/Inbox notified for: {data.slug}", "yellow")
        else:
            log(
                f"⚠️ Discord/Inbox notification failed → {webhook_res.status_code}",
                "yellow",
            )
    except Exception as e:
        log(f"⚠️ Discord/Inbox notification error: {e}", "yellow")

    log(f"✅ Sign pipeline finished for: {data.slug}", "green")
    return {"status": "signed", "slug": data.slug}


@app.post("/pipeline")
def run_pipeline(data: SlugRequest):
    import json
    from pathlib import Path
    from urllib.parse import quote

    import requests
    import yaml
    from markdown import markdown

    slug = data.slug
    log(f"🚀 Starting pipeline for: {slug}", "magenta")

    # Log to signed.json
    signed_log = Path("vault/personas/.signed.json")
    signed_data = {}
    if signed_log.exists():
        with open(signed_log) as f:
            signed_data = json.load(f)
    signed_data[slug] = {"status": "signed"}
    with open(signed_log, "w") as f:
        json.dump(signed_data, f, indent=2)

    # Generate .mdx
    source = Path(f"vault/personas/{slug}.yml")
    if not source.exists():
        return {"error": "YAML not found", "slug": slug}
    with open(source) as f:
        persona = yaml.safe_load(f)
    mdx_dir = Path("vault/personas/mdx")
    mdx_dir.mkdir(parents=True, exist_ok=True)
    mdx_path = mdx_dir / f"{slug}.mdx"
    content = f"""---
title: "{slug}"
description: "{persona.get('description', '')}"
traits: {persona.get('traits', [])}
---

# {slug}

{persona.get('prompt', '')}
"""
    with open(mdx_path, "w") as f:
        f.write(content)
    log(f"📝 .mdx written: {mdx_path}", "green")

    # Generate .html preview
    html = markdown(content)
    html_path = mdx_dir / f"{slug}.html"
    with open(html_path, "w") as f:
        f.write(f"<html><body>{html}</body></html>")
    log(f"🌐 HTML preview saved: {html_path}", "green")

    # Trigger deploys
    try:
        encoded = quote(slug)
        res = requests.post(
            f"http://localhost:8004/explorer/deploy?slug={encoded}", timeout=5
        )
        log(f"📡 Explorer {res.status_code}", "yellow")
    except Exception as e:
        log(f"❌ Explorer error: {e}", "red")

    try:
        pub = requests.post(
            "http://localhost:8005/vault/publish", json={"slug": slug}, timeout=5
        )
        log(f"📦 IPFS/Arweave {pub.status_code}", "green")
    except Exception as e:
        log(f"❌ Publish error: {e}", "red")

    try:
        note = requests.post(
            "http://localhost:8006/notify",
            json={"slug": slug, "event": "pipeline-complete"},
            timeout=5,
        )
        log(f"🔔 Notified {note.status_code}", "yellow")
    except Exception as e:
        log(f"❌ Notify error: {e}", "red")

    # Log to .deployed.json
    deployed_log = Path("vault/personas/.deployed.json")
    deployed = {}
    if deployed_log.exists():
        with open(deployed_log) as f:
            deployed = json.load(f)
    deployed[slug] = {"status": "deployed"}
    with open(deployed_log, "w") as f:
        json.dump(deployed, f, indent=2)

    log(f"✅ Pipeline fully complete for: {slug}", "green")
    return {"status": "complete", "slug": slug}
