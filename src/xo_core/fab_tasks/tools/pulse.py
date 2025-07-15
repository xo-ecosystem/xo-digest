from invoke import task, Collection


@task
def validate(c, path="content/pulses"):
    """
    ✅ Validate pulse .mdx or .yml files in content/pulses/
    """
    import pathlib

    import yaml

    base = pathlib.Path(path)
    for file in base.glob("*.xo-seed.yml"):
        try:
            with open(file) as f:
                yaml.safe_load(f)
            print(f"✅ {file} is valid.")
        except Exception as e:
            print(f"❌ {file} failed: {e}")


@task
def describe(c, path="content/pulses"):
    """
    📄 Print a summary of pulse metadata from .xo-seed.yml files.
    """
    import pathlib

    import yaml

    base = pathlib.Path(path)
    for file in base.glob("*.xo-seed.yml"):
        try:
            with open(file) as f:
                data = yaml.safe_load(f)
            print(f"\n🔎 {file.name}")
            print(f"  • title: {data.get('title')}")
            print(f"  • tags: {', '.join(data.get('tags', []))}")
        except Exception as e:
            print(f"⚠️  Failed to read {file.name}: {e}")


# Create namespace
ns = Collection("pulse")
ns.add_task(validate)
ns.add_task(describe)
