from invoke import Collection, task


@task
def start(c):
    """🧠 Start Agent0 runtime"""
    print("Starting Agent0...")


@task
def generate_mdx(c):
    source_dir = Path("vault/personas")
    target_dir = source_dir / "mdx"
    target_dir.mkdir(parents=True, exist_ok=True)

    for yml_file in sorted(source_dir.glob("*.yml")):
        with open(yml_file) as f:
            data = yaml.safe_load(f)

        name = data.get("name", yml_file.stem)
        mdx_path = target_dir / f"{name}.mdx"

        content = f"""---
title: "{name}"
description: "{data.get('description', '')}"
traits: {data.get('traits', [])}
---

# {name}

{data.get('prompt', 'No prompt provided.')}

"""

        with open(mdx_path, "w") as out:
            out.write(content)

        print(f"📝 Generated: {mdx_path}")


ns = Collection("agent0")
ns.add_task(start)
ns.add_task(generate_mdx, name="generate-mdx")
