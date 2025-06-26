#!/usr/bin/env python3
import os
import stat


def setup_pre_commit_hook():
    hook_path = os.path.join(".git", "hooks", "pre-commit")
    hook_content = """#!/bin/sh
echo "🔒 Pre-commit check: preventing .venv/.direnv from being committed..."
if git diff --cached --name-only | grep -E '^(venv|\\.venv|\\.direnv)/'; then
  echo "❌ Commit blocked: virtual environment files detected in staging area."
  exit 1
fi
"""
    # Write the pre-commit hook
    with open(hook_path, "w") as hook_file:
        hook_file.write(hook_content)
    # Make it executable
    st = os.stat(hook_path)
    os.chmod(hook_path, st.st_mode | stat.S_IEXEC)


def setup_gitattributes():
    gitattributes_path = ".gitattributes"
    entries = [
        ".venv/ binary",
        "venv/ binary",
        ".direnv/ binary",
    ]
    # Read existing lines if file exists
    existing_lines = []
    if os.path.exists(gitattributes_path):
        with open(gitattributes_path) as f:
            existing_lines = [line.strip() for line in f.readlines()]
    # Append missing entries
    with open(gitattributes_path, "a") as f:
        for entry in entries:
            if entry not in existing_lines:
                f.write(entry + "\n")


def main():
    setup_pre_commit_hook()
    setup_gitattributes()
    print(
        "✅ Git hooks and .gitattributes configured to prevent committing virtual environment files."
    )


if __name__ == "__main__":
    main()
