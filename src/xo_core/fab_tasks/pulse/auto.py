from invoke import task, Collection

@task(help={
    "slug": "Slug name for the pulse (default: test_pulse)",
    "dry_run": "Use dry-run for archive step"
})
def auto(c, slug="test_pulse", dry_run=False):
    """
    🤖 Automated pulse workflow: generate → sign → sync → archive → bundle
    """
    print(f"🤖 Starting automated pulse workflow for: {slug}")
    
    steps = [
        ("Generate test pulse", f"xo-fab pulse.new --slug {slug}"),
        ("Sign pulse", f"xo-fab pulse.sign --slug {slug}"),
        ("Sync pulse", f"xo-fab pulse.sync --slug {slug}"),
        ("Archive pulse", f"xo-fab pulse.archive --slug {slug} --dry-run" if dry_run else f"xo-fab pulse.archive --slug {slug}"),
        ("Bundle vault outputs", "xo-fab bundle.bundle-sync")
    ]
    
    completed = 0
    total_steps = len(steps)
    
    for step_name, command in steps:
        try:
            print(f"\n🔄 {step_name}...")
            result = c.run(command, warn=True)
            if result.ok:
                print(f"✅ {step_name} completed")
                completed += 1
            else:
                print(f"⚠️ {step_name} had issues (continuing...)")
                print(f"   Command: {command}")
                print(f"   Exit code: {result.exited}")
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
            print(f"   Command: {command}")
            # Continue with next step instead of failing completely
    
    print(f"\n🏁 Pulse automation complete!")
    print(f"📊 Steps completed: {completed}/{total_steps}")
    
    if completed == total_steps:
        print("🎉 All steps completed successfully!")
    else:
        print("⚠️ Some steps had issues - check output above")

# Register for dynamic loader
ns = Collection()
ns.add_task(auto)

__all__ = ["ns"] 