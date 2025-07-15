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


# Create namespace
ns = Collection("lint")
ns.add_task(validate)
