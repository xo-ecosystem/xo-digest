from invoke import task, Collection

def _lazy_generate_test_pulse(c, slug):
    """Lazy import and call generate_test_pulse to avoid circular imports."""
    try:
        from ._shared_data import generate_test_pulse as _generate
    except ImportError:
        # Fallback for script execution
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from _shared_data import generate_test_pulse as _generate
    
    result = _generate(c, slug)
    print(f"🧪 Generated test pulse: {result.get('slug', slug)}")
    return result

@task(help={"slug": "Slug name of the pulse to create"})
def new(c, slug):
    if slug == "test_pulse":
        _lazy_generate_test_pulse(c, slug)

    pulse_path = f"content/pulses/{slug}/{slug}.mdx"
    from pathlib import Path
    Path(pulse_path).parent.mkdir(parents=True, exist_ok=True)
    if not Path(pulse_path).exists():
        Path(pulse_path).write_text(f"# New Pulse: {slug}", encoding="utf-8")
        print(f"✅ New pulse created at: {pulse_path}")
    else:
        print(f"ℹ️ Pulse already exists: {pulse_path}")

@task
def new_pulse(c, slug=None):
    """Create a new pulse .mdx file."""
    if not slug:
        print("❌ Missing required --slug argument.")
        return

    print(f"🔧 Creating new pulse for slug: {slug}")
    
    if slug == "test_pulse":
        _lazy_generate_test_pulse(c, slug)

    pulse_path = f"content/pulses/{slug}/{slug}.mdx"
    from pathlib import Path
    Path(pulse_path).parent.mkdir(parents=True, exist_ok=True)
    if not Path(pulse_path).exists():
        Path(pulse_path).write_text(f"# New Pulse: {slug}", encoding="utf-8")
        print(f"✅ New pulse created at: {pulse_path}")
    else:
        print(f"ℹ️ Pulse already exists: {pulse_path}")

# Create namespace
ns = Collection("new")
ns.add_task(new)
ns.add_task(new_pulse)
