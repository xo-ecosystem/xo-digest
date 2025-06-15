from invoke import task


@task
def cz_lint(c):
    """Run commitizen check, coverage badge, and static type checking."""
    try:
        c.run("cz check", pty=False)
        c.run("coverage-badge -o coverage.svg")
        c.run("mypy .")
        c.run("cz changelog --dry-run", pty=False)
    except Exception as e:
        print(f"Error during linting: {e}")
        raise

    # Validate that the generated changelog wouldn't crash
    c.run("cz changelog --dry-run", pty=True)

    # Optional extras – uncomment / add whatever you need
    # c.run("pytest --cov=vault --cov-report=term-missing")
