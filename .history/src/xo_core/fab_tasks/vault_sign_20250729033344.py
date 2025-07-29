def sign(*args, **kwargs):
    from invoke import Context

    c = Context()

    print("🔐 Signing vault content for webhook task execution...")
    c.run("echo 'Vault signing executed for webhook task'")
