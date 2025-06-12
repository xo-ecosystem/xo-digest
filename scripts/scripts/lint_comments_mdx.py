import os
import re
from datetime import datetime
from pathlib import Path

COMMENT_DIR = Path("content/comments")

DEFAULT_METADATA = """<!--
author: unknown
slug: your-comment-id
date: YYYY-MM-DD
-->
"""


def lint_comment_file(file_path):
    with open(file_path, "r+", encoding="utf-8") as f:
        content = f.read()

        if not content.strip():
            print(f"⚠️  Empty comment file — inserting default metadata in: {file_path}")
            f.seek(0)
            f.write(DEFAULT_METADATA + "\n\n## Comment\n\nYour comment here...\n")
            f.truncate()
            print("📌 Default metadata inserted.")
            return False

        if not content.startswith("<!--") or "-->" not in content:
            print(f"⚠️  Missing metadata block — auto-inserting in: {file_path}")
            content = DEFAULT_METADATA + "\n" + content
            f.seek(0)
            f.write(content)
            f.truncate()
            print("📌 Default metadata inserted.")
            return False

        meta_block = content.split("-->", 1)[0]

        required_tags = ["author", "date", "slug"]
        for tag in required_tags:
            if f"{tag}:" not in meta_block:
                print(f"⚠️  Missing {tag} tag in: {file_path}")
                content = DEFAULT_METADATA + "\n" + content
                f.seek(0)
                f.write(content)
                f.truncate()
                print("📌 Default metadata inserted.")
                return False

        # Warn if author or slug appears as "unknown" or placeholder
        for tag in ["author", "slug"]:
            match = re.search(rf"{tag}:\s*(\S+)", meta_block)
            if match and match.group(1) in {"unknown", "your-comment-id"}:
                print(f"⚠️  Placeholder {tag} tag in: {file_path} → {match.group(1)}")

        # Additional validation for date format
        date_match = re.search(r"date:\s*(\S+)", meta_block)
        if date_match:
            date_value = date_match.group(1)
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                print(f"⚠️  Malformed date format in: {file_path} → {date_value}")

        if "reply_to:" in meta_block:
            reply_id = re.search(r"reply_to:\s*(\S+)", meta_block)
            if not reply_id:
                print(f"⚠️  Malformed reply_to field in: {file_path}")

        if "## Reply" not in content and "## Comment" not in content:
            print(f"⚠️  Missing section header in: {file_path}")

        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags
            "]+",
            flags=re.UNICODE,
        )
        emoji_matches = emoji_pattern.findall(content)
        if emoji_matches:
            print(f"⚠️  Contains emojis in: {file_path} → {emoji_matches}")

        # Optional: enforce emoji whitelist
        allowed_emojis = {"👍", "❤️", "🚀"}
        disallowed = [e for e in emoji_matches if e not in allowed_emojis]
        if disallowed:
            print(f"⚠️  Disallowed emojis in: {file_path} → {disallowed}")

        # Check for minimum metadata completeness
        if not all(tag + ":" in meta_block for tag in ["author", "slug", "date"]):
            print(f"⚠️  Incomplete metadata block in: {file_path}")

        if len(content.strip()) < 50:
            print(f"⚠️  Very short comment in: {file_path}")

        broken_links = re.findall(r"\[.*?\]\((.*?)\)", content)
        broken_images = re.findall(r"!\[.*?\]\((.*?)\)", content)
        for link in broken_links + broken_images:
            if not link or not re.match(r"https?://", link):
                print(
                    f"⚠️  Possibly broken or empty link/image in: {file_path} → {link}"
                )

        if "[reaction:" in content:
            reaction_tags = re.findall(r"\[reaction:(.*?)\]", content)
            if not reaction_tags:
                print(f"⚠️  Malformed reaction tag in: {file_path}")
            else:
                print(f"💬 Found reaction tags in: {file_path} → {reaction_tags}")

        # Optional: check for invalid slug formats
        slug_match = re.search(r"slug:\s*(\S+)", meta_block)
        if slug_match:
            slug_value = slug_match.group(1)
            if not re.match(r"^[a-z0-9\-]+$", slug_value):
                print(f"⚠️  Invalid slug format in: {file_path} → {slug_value}")

        # Check if reply_to has invalid characters
        if "reply_to:" in meta_block:
            reply_match = re.search(r"reply_to:\s*(\S+)", meta_block)
            if reply_match:
                reply_id = reply_match.group(1)
                if not re.match(r"^[a-z0-9\-]+$", reply_id):
                    print(f"⚠️  Invalid reply_to format in: {file_path} → {reply_id}")

    print(f"✅ Passed: {file_path}")
    return True


def run_linter():
    if not COMMENT_DIR.exists():
        COMMENT_DIR.mkdir(parents=True, exist_ok=True)
        print("📁 Created missing comment directory at content/comments")

    total = 0
    failed = 0
    for mdx_file in COMMENT_DIR.glob("**/*.comments.mdx"):
        total += 1
        if not lint_comment_file(mdx_file):
            failed += 1

    print(f"\n🧾 Lint Summary: {total} file(s) checked, {failed} issue(s) found.")
    print("🧠 Enforcing metadata fields (slug/date) and validating structure...")
    print("🧪 Threading tree, reply ID, and slug format checks complete.")
    build_reply_tree()


# Render nested threaded reply tree for comments
def build_reply_tree():
    from collections import defaultdict

    # Map of slug → comment content + metadata
    comment_data = {}
    children = defaultdict(list)

    for mdx_file in COMMENT_DIR.glob("**/*.comments.mdx"):
        with open(mdx_file, encoding="utf-8") as f:
            content = f.read()
            slug_match = re.search(r"slug:\s*(\S+)", content)
            reply_to_match = re.search(r"reply_to:\s*(\S+)", content)
            slug = slug_match.group(1) if slug_match else mdx_file.stem
            reply_to = reply_to_match.group(1) if reply_to_match else None
            comment_data[slug] = {"file": str(mdx_file), "reply_to": reply_to}
            if reply_to:
                children[reply_to].append(slug)

    def print_tree(slug, depth=0):
        indent = "  " * depth
        print(f"{indent}↪ {slug} ({comment_data[slug]['file']})")
        for child in children.get(slug, []):
            print_tree(child, depth + 1)

    print("\n🧬 Comment Threading Tree:")
    roots = [s for s in comment_data if comment_data[s]["reply_to"] is None]
    for root in roots:
        print_tree(root)


# Auto-run comment rendering and threading export
import subprocess  # nosec


def post_lint_tasks():
    print("\n🔁 Running post-lint tasks...")
    subprocess.run(["python", "scripts/render_comments_html.py"], check=False)  # nosec
    subprocess.run(["python", "scripts/export_replies.py"], check=False)  # nosec
    if Path("scripts/score_comments.py").exists():
        subprocess.run(["python", "scripts/score_comments.py"], check=False)  # nosec
    else:
        print("⚠️  score_comments.py not found, skipping scoring...")
    extract_scores()


def extract_scores():
    print("\n📊 Extracting emoji-based scores with decay...")
    score_weights = {"❤️": 3, "🚀": 5, "👍": 1}
    today = datetime.now()

    for mdx_file in COMMENT_DIR.glob("**/*.comments.mdx"):
        with open(mdx_file, encoding="utf-8") as f:
            content = f.read()
            reactions = re.findall(r"\[reaction:([^\]]+)\]", content)
            base_score = 0
            for reaction in reactions:
                for emoji, weight in score_weights.items():
                    if emoji in reaction:
                        count_match = re.search(rf"{emoji}\s*x(\d+)", reaction)
                        count = int(count_match.group(1)) if count_match else 1
                        base_score += weight * count

            date_match = re.search(r"date:\s*(\S+)", content)
            age_days = 0
            if date_match:
                try:
                    comment_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                    age_days = (today - comment_date).days
                except ValueError:
                    print(f"⚠️  Malformed date format in: {mdx_file}")

            decay_factor = 1 / (1 + age_days / 7) if age_days > 0 else 1
            final_score = round(base_score * decay_factor, 2)

            score_file = mdx_file.with_suffix(".score.json")
            with open(score_file, "w", encoding="utf-8") as out:
                out.write(
                    f'{{"score": {final_score}, "age_days": {age_days}, "decayed": true}}'
                )
            print(f"⭐ Decayed Score {final_score} → {score_file}")


if __name__ == "__main__":
    run_linter()
    post_lint_tasks()
    subprocess.run(["python", "scripts/render_dashboard.py"], check=False)  # nosec
    print(
        "✅ All post-lint tasks completed including preview render, score sync, and reply tree export."
    )
