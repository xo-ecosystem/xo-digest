from invoke import task, Collection
from xo_core.vault.inbox import send_to_xo_inbox

@task
def send(c, slug):
    """
    📨 Send vault digest or pin summary to XO Inbox
    """
    manifest_path = f"vault/.pins/pin_manifest.json"
    message = f"📬 New pin summary for `{slug}` posted to XO Inbox."
    send_to_xo_inbox(message=message, manifest_path=manifest_path, slug=slug)

ns = Collection()
ns.add_task(send)