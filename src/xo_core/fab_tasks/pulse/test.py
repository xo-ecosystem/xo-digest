"""
Simple stub for pulse.test to avoid recursion issues.
This provides basic test functionality without circular imports.
"""

from invoke import task, Collection


@task(help={"slug": "Slug of the pulse to test"})
def test_pulse(c, slug="test_pulse"):
    """
    🧪 Test a pulse by running basic validation checks.
    """
    print(f"🧪 Testing pulse: {slug}")
    
    from pathlib import Path
    
    # Check if pulse files exist
    pulse_dir = Path(f"content/pulses/{slug}")
    if not pulse_dir.exists():
        print(f"❌ Pulse directory not found: {pulse_dir}")
        return False
    
    mdx_file = pulse_dir / f"{slug}.mdx"
    if not mdx_file.exists():
        print(f"❌ Pulse MDX file not found: {mdx_file}")
        return False
    
    print(f"✅ Pulse files found: {mdx_file}")
    
    # Basic content validation
    try:
        content = mdx_file.read_text()
        if len(content.strip()) < 10:
            print("⚠️ Pulse content seems very short")
        else:
            print(f"✅ Pulse content looks good ({len(content)} chars)")
    except Exception as e:
        print(f"❌ Error reading pulse content: {e}")
        return False
    
    return True


@task
def test_all(c):
    """
    🧪 Test all pulses in the content/pulses directory.
    """
    print("🧪 Testing all pulses...")
    
    from pathlib import Path
    
    pulses_dir = Path("content/pulses")
    if not pulses_dir.exists():
        print("❌ No pulses directory found")
        return
    
    results = []
    for pulse_dir in pulses_dir.iterdir():
        if pulse_dir.is_dir() and not pulse_dir.name.startswith('.'):
            slug = pulse_dir.name
            print(f"\n🔍 Testing {slug}...")
            result = test_pulse(c, slug)
            results.append((slug, result))
    
    # Summary
    print("\n📊 Test Results:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for slug, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {slug}")
    
    print(f"\n🎯 Overall: {passed}/{total} pulses passed")
    return passed == total


def generate_test_pulse():
    """
    Generates a test pulse directory and file for validation purposes.
    """
    from pathlib import Path

    slug = "test_pulse"
    pulse_dir = Path(f"content/pulses/{slug}")
    pulse_dir.mkdir(parents=True, exist_ok=True)

    mdx_file = pulse_dir / f"{slug}.mdx"
    if not mdx_file.exists():
        mdx_file.write_text(f"# {slug}\n\nThis is a test pulse.")
        print(f"✅ Created test pulse at: {mdx_file}")
    else:
        print(f"ℹ️ Test pulse already exists at: {mdx_file}")


# Create namespace
ns = Collection("test")
ns.add_task(test_pulse)
ns.add_task(test_all)