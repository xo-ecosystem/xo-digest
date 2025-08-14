from invoke import task


@task
def static(c, drop="message_bottle"):
    """
    Build static socials page for given drop.
    Default: message_bottle
    """
    print(f"🚀 Building static socials for drop={drop}...")
    cmd = f"python3 scripts/render_socials_static.py"
    c.run(cmd, pty=True)
    print("✅ Static socials build complete.")
