import requests

from xo_core.config import WEBHOOK_URL

def scaffold_persona_folder(persona):
    from pathlib import Path
    base = Path(f"vault/constellation/{persona}")
    base.mkdir(parents=True, exist_ok=True)
    (base / "inbox_preview.mdx").write_text(f"# 🪐 Inbox Preview for {persona}\n\n")
    (base / "reply_stub.mdx").write_text(f"# 💬 Suggested Replies for {persona}\n\n> Placeholder reply\n")
    (base / "persona.yml").write_text(f"name: {persona}\ndescription: ''\ntraits: []\n")
    print(f"✨ Scaffolded persona folder: {base}")
    # Auto-generate a basic lore intro and NFT metadata file
    (base / "lore_intro.mdx").write_text(f"# ✨ Lore of {persona}\n\nOnce upon a pulse...\n")
    (base / "nft_metadata.json").write_text(f"""{{
        "name": "{persona}",
        "description": "A unique XO persona sealed within the constellation.",
        "image": "ipfs://placeholder",
        "attributes": []
    }}""")

# --- Webhook sending utility
def send_to_webhook(payload: dict, webhook_url: str):
    try:
        response = requests.post(webhook_url, json=payload)
        print(f"✅ Webhook sent: {response.status_code}")
    except Exception as e:
        print(f"❌ Webhook error: {e}")

from xo_core.agent.inbox_listener import listen_to_inbox

def launch_persona_listener(persona: str, webhook=False, preview=False, memory=False):
    print(f"🔮 Launching inbox listener for persona: {persona}")
    scaffold_persona_folder(persona)
    messages = listen_to_inbox(persona)
    # Ensure messages is a list of dicts; if not, mock or convert accordingly
    if not isinstance(messages, list):
        messages = [messages]
    for message in messages:
        if preview:
            print(f"🪞 Preview: [{message.get('sender')}] {message.get('text')}")
        if webhook:
            send_to_webhook(message, webhook_url=WEBHOOK_URL)
        if memory:
            # Simulate saving message to persona memory (append to a file or Vault stub)
            memory_path = f"vault/.memory/{persona}.mdx"
            with open(memory_path, "a") as f:
                f.write(f"- [{message.get('sender')}] {message.get('text')}\n")
            print(f"🧠 Logged to memory: {memory_path}")
            if preview:
                constellation_preview_path = f"vault/constellation/{persona}/inbox_preview.mdx"
                from pathlib import Path
                Path(constellation_preview_path).parent.mkdir(parents=True, exist_ok=True)
                with open(constellation_preview_path, "w") as preview_file:
                    preview_file.write(f"# 🪐 Inbox Preview for {persona}\n\n")
                    for msg in messages:
                        preview_file.write(f"- **{msg.get('sender')}**: {msg.get('text')}\n")
                print(f"🌌 Preview written to: {constellation_preview_path}")
        # Add logic to store replies for future stubs in the Vault
        if memory:
            reply_stub_path = f"vault/constellation/{persona}/reply_stub.mdx"
            from pathlib import Path
            Path(reply_stub_path).parent.mkdir(parents=True, exist_ok=True)
            with open(reply_stub_path, "w") as f:
                f.write(f"# 💬 Suggested Replies for {persona}\n\n")
                f.write(f'> Placeholder reply for message: "{message.get("text")}"\n')
            print(f"✏️ Reply stub saved to: {reply_stub_path}")
    print("📡 Ready with webhook forwarding, message previews, and basic memory logging.")
    if webhook:
        print("📡 Webhook forwarding enabled.")
    if preview:
        print("🪞 Message preview mode active.")
    if memory:
        print("🧠 Memory linkage enabled.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Launch XO Persona Listener")
    parser.add_argument("--persona", required=True, help="Name of the XO persona")
    parser.add_argument("--webhook", action="store_true", help="Enable webhook forwarding")
    parser.add_argument("--preview", action="store_true", help="Enable message previews")
    parser.add_argument("--memory", action="store_true", help="Enable linked memory features")
    args = parser.parse_args()

    launch_persona_listener(
        args.persona,
        webhook=args.webhook,
        preview=args.preview,
        memory=args.memory
    )

from invoke import task

@task(help={
    "persona": "Name of the XO persona",
    "webhook": "Enable webhook forwarding",
    "preview": "Enable message previews",
    "memory": "Enable linked memory"
})
def inbox_listen(c, persona, webhook=False, preview=False, memory=False):
    """
    Launch inbox listener for a specific XO persona
    Usage: fab inbox.listen --persona=seal_dream [--webhook] [--preview] [--memory]
    """
    launch_persona_listener(persona, webhook=webhook, preview=preview, memory=memory)