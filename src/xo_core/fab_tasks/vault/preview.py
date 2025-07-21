
from invoke import task, Collection
from xo_core.utils.pulse_loader import load_all_pulses
from xo_core.vault.preview_generator import render_signed_preview

@task
def preview_all(c):
    print("🧪 Generating all vault previews...")
    pulses = load_all_pulses()
    for pulse in pulses:
        output_path = f"vault/preview/{pulse['slug']}.html"
        render_signed_preview(pulse, output_path)

ns = Collection("preview")
ns.add_task(preview_all, name="all")
