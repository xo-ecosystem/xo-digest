def render_task_summary(tasks):
    """
    Convert a list of Invoke tasks to a markdown summary.
    """
    lines = ["# XO Task Summary\n"]
    for task in tasks:
        lines.append(f"## `{task.name}`")
        lines.append(f"{task.__doc__.strip() if task.__doc__ else 'No description.'}")
        lines.append("")
    return "\n".join(lines)
def save_task_summary_to_file(tasks, filepath):
    """
    Render the task summary and save it to a file.
    """
    content = render_task_summary(tasks)
    with open(filepath, "w") as f:
        f.write(content)