from pathlib import Path
import frontmatter

def load_all_pulses(base_dir="content/pulses"):
    pulse_paths = list(Path(base_dir).rglob("index.mdx"))
    pulses = []
    for path in pulse_paths:
        post = frontmatter.load(path)
        pulse = {
            "slug": path.parent.name,
            "title": post.get("title", "Untitled"),
            "content": post.content,
            "metadata": post.metadata,
            "path": str(path)
        }
        pulses.append(pulse)
    return pulses