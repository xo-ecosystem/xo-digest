from invoke import task
import subprocess


@task
def purge_tracked_ignored(c):
    """
    🚫 Remove all files that are tracked by git but now ignored by .gitignore.
    Use with caution: this will DELETE files!
    """
    print("🧹 Scanning for tracked but ignored files...")
    try:
        # List all tracked files that are now ignored
        result = subprocess.run(
            ["git", "ls-files", "--ignored", "--exclude-standard", "--cached"],
            capture_output=True,
            text=True,
            check=True,
        )
        ignored_files = result.stdout.strip().splitlines()

        if not ignored_files:
            print("✅ No ignored tracked files to remove.")
            return

        print("🚫 Removing the following files from git tracking:")
        for file in ignored_files:
            print(f"  - {file}")

        # Remove them from git cache
        subprocess.run(["git", "rm", "--cached"] + ignored_files, check=True)
        print("✅ Successfully purged ignored tracked files.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during purge: {e.stderr}")


from invoke import Collection

ns = Collection("git")
ns.add_task(purge_tracked_ignored)
