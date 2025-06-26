import io
import sys

from fabric import Config
from invoke import Collection, task


@task(optional=["to_md", "save_to", "filter"])
def summary(c, to_md=False, save_to=None, filter=None):
    """
    📄 Show all registered Fabric tasks grouped by namespace.
    Optional:
      --to-md: Render as Markdown
      --save-to=<filename>: Save output to file
      --filter=<namespace>: Only show matching namespaces
    """
    from xo_core.fabfile import ns as root_ns

    buffer = io.StringIO()
    output = buffer if to_md or save_to else sys.stdout

    def render(ns, prefix=""):
        for name, task_obj in ns.tasks.items():
            full_name = f"{prefix}{name}"
            if filter and not full_name.startswith(filter):
                continue
            doc = (task_obj.__doc__ or "").strip()
            if to_md or save_to:
                print(f"- `{full_name}`: {doc}", file=output)
            else:
                print(f"{full_name:<30}  {doc}", file=output)
        for subname, subns in ns.collections.items():
            render(subns, prefix=f"{prefix}{subname}.")

    render(root_ns)

    if save_to:
        with open(save_to, "w") as f:
            f.write(buffer.getvalue())
        print(f"✅ Task summary saved to {save_to}")
