import zipfile
from pathlib import Path


def create_digest_zip(date_str: str, output_dir: Path = Path("vault/daily")) -> Path:
    zip_path = output_dir / f"{date_str}.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        html_path = output_dir / "index.html"
        slim_md_path = output_dir / f"{date_str}.slim.md"
        if html_path.exists():
            zipf.write(html_path, arcname="index.html")
        if slim_md_path.exists():
            zipf.write(slim_md_path, arcname=f"{date_str}.slim.md")
    return zip_path
