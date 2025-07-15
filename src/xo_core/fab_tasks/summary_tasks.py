from invoke import task, Collection
from xo_core.utils.task_registry import all_registered_tasks
from xo_core.utils.markdown import render_task_summary

@task(help={'save_to': "Path to save markdown output"})
def to_md(c, save_to=None):
    """Generate Markdown summary of all tasks."""
    summary = render_task_summary(all_registered_tasks())
    if save_to:
        import os

        # Ensure target directory exists
        os.makedirs(os.path.dirname(save_to), exist_ok=True)

        with open(save_to, 'w') as f:
            f.write(summary)
        print(f"✅ Saved task summary to: {save_to}")
    else:
        print(summary)

ns = Collection("summary")
ns.add_task(to_md, name="to-md")

__all__ = ["ns"]