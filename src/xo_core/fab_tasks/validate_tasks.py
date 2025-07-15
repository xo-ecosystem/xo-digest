import argparse
import importlib.util
import shlex
import sys
from pathlib import Path

from invoke import Context, task


def validate_all_tasks(verbose=False):
    task_dir = Path(__file__).parent
    failures = []
    for py_file in sorted(task_dir.glob("*.py")):
        if py_file.name.startswith("_") or py_file.name in [
            "fabfile.py",
            "__init__.py",
        ]:
            continue
        module_name = py_file.stem
        try:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ Imported: {module_name}")
        except Exception as e:
            if verbose:
                import traceback

                traceback.print_exc()
            else:
                print(f"❌ Failed: {module_name} — {e}")
            failures.append(module_name)
    return failures


@task(iterable=["flags"])
def validate_tasks(c, flags=None):
    """
    🔍 Validate import of all Fabric task modules in fab_tasks/
    Usage:
        fab validate_tasks
        fab validate_tasks:flags=--verbose
        fab validate_tasks:flags="--verbose --fail-on-error"
    """
    flags = flags or []
    args = shlex.split(" ".join(flags))
    verbose = "--verbose" in args
    fail_on_error = "--fail-on-error" in args

    failures = validate_all_tasks(verbose=verbose)
    if failures:
        print(f"❌ Validation failed for: {', '.join(failures)}")
        if fail_on_error:
            sys.exit(1)
    else:
        print("✅ Task validation completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Fabric task modules.")
    parser.add_argument(
        "--verbose", action="store_true", help="Show full tracebacks on import errors."
    )
    parser.add_argument(
        "--fail-on-error", action="store_true", help="Exit with code 1 on any failure."
    )
    args = parser.parse_args()

    failures = validate_all_tasks(verbose=args.verbose)
    if failures:
        print(f"❌ Validation failed for: {', '.join(failures)}")
        if args.fail_on_error:
            sys.exit(1)
    else:
        print("✅ Task validation completed.")


@task
def validate_all(c):
    """
    ✅ Validate all fab_tasks/* modules for import errors.
    Alias: xo-fab pulse.validate-all
    """
    failures = validate_all_tasks(verbose=True)
    if failures:
        print(f"❌ Validation failed for: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("✅ All fab_tasks modules imported successfully.")

from invoke import Collection

ns = Collection("validate")
ns.add_task(validate_tasks, name="tasks")
ns.add_task(validate_all, name="all")

__all__ = ["ns"]
