from invoke import Collection, task
import os
import shutil
import subprocess
from datetime import datetime


@task
def bundle(c, output_dir="patch_bundle", include_logs=True):
    """
    Create a patch bundle with changes, task summary, and optional logs.

    Args:
        output_dir (str): Directory to create bundle in
        include_logs (bool): Include logs directory in bundle
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_name = f"xo_core_patch_{timestamp}"
    bundle_path = os.path.join(output_dir, bundle_name)

    print(f"📦 Creating patch bundle: {bundle_path}")

    # Create bundle directory
    os.makedirs(bundle_path, exist_ok=True)

    # Generate git diff patch
    try:
        patch_file = os.path.join(bundle_path, "changes.patch")
        result = subprocess.run(
            ["git", "diff", "--cached", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            with open(patch_file, "w") as f:
                f.write(result.stdout)
            print(f"✅ Created patch file: {patch_file}")
        else:
            print("ℹ️ No changes to patch")
    except Exception as e:
        print(f"⚠️ Could not create patch: {e}")

    # Create task summary
    summary_file = os.path.join(bundle_path, f"task_summary_{timestamp}.md")
    with open(summary_file, "w") as f:
        f.write(f"# XO Core Patch Bundle - {timestamp}\n\n")
        f.write("## Changes Included\n")
        f.write("- DNS configuration updates\n")
        f.write("- Deploy automation improvements\n")
        f.write("- Service synchronization\n")
        f.write("- Environment variable sync\n")
        f.write("- Dashboard integration\n\n")
        f.write("## Services\n")
        f.write("- vault.21xo.com\n")
        f.write("- inbox.21xo.com\n")
        f.write("- preview.21xo.com\n")
        f.write("- agent0.21xo.com\n")

    print(f"✅ Created task summary: {summary_file}")

    # Include logs if requested
    if include_logs and os.path.exists("logs"):
        logs_dest = os.path.join(bundle_path, "logs")
        shutil.copytree("logs", logs_dest, dirs_exist_ok=True)
        print(f"✅ Included logs directory")

    # Create ZIP archive
    zip_path = f"{bundle_path}.zip"
    shutil.make_archive(bundle_path, "zip", bundle_path)
    print(f"✅ Created ZIP archive: {zip_path}")

    return bundle_path


@task
def apply(c, bundle_path):
    """
    Apply a patch bundle.

    Args:
        bundle_path (str): Path to the patch bundle to apply
    """
    print(f"🔧 Applying patch bundle: {bundle_path}")

    if not os.path.exists(bundle_path):
        print(f"❌ Bundle not found: {bundle_path}")
        return

    # Extract if it's a ZIP
    if bundle_path.endswith(".zip"):
        import zipfile

        extract_path = bundle_path[:-4]
        with zipfile.ZipFile(bundle_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        bundle_path = extract_path

    # Apply patch if exists
    patch_file = os.path.join(bundle_path, "changes.patch")
    if os.path.exists(patch_file):
        try:
            subprocess.run(["git", "apply", patch_file], check=True)
            print("✅ Applied patch successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to apply patch: {e}")

    print("✅ Patch bundle applied")


# Create namespace

ns = Collection("patch")
ns.add_task(bundle, "bundle")
ns.add_task(apply, "apply")


# Patch hook function
def apply_patch(bundle_path="patch_bundle"):
    """
    Apply patch from the given bundle path.
    Used by webhook agent hook system.
    """
    import os
    import subprocess

    patch_file = os.path.join(bundle_path, "changes.patch")
    if os.path.exists(patch_file):
        try:
            subprocess.run(["git", "apply", patch_file], check=True)
            print("✅ Patch hook applied from:", patch_file)
        except subprocess.CalledProcessError as e:
            print("❌ Patch hook failed:", e)
    else:
        print("⚠️ No patch file found in bundle path:", patch_file)
