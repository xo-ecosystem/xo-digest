from invoke import task

@task(help={"dry": "Only list matching images without converting"})
def webp(c, dry=False):
    """
    Convert images in drop.assets/eighth to .webp format.
    """
    import os
    from pathlib import Path
    from PIL import Image

    folder = Path("drop.assets/eighth")
    if not folder.exists():
        print("❌ Folder not found:", folder)
        return

    images = list(folder.glob("*.png"))
    if dry:
        for img in images:
            print(f"🔍 Would convert: {img.name} → {img.with_suffix('.webp').name}")
        return

    for img_path in images:
        webp_path = img_path.with_suffix(".webp")
        try:
            with Image.open(img_path) as im:
                im.save(webp_path, "WEBP")
            print(f"✅ Converted {img_path.name} → {webp_path.name}")
        except Exception as e:
            print(f"⚠️ Failed to convert {img_path.name}: {e}")