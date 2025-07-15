import json
import importlib
import inspect
from fabric import task
from xo_core.fab_tasks import digest, vault_tasks, utils

modules = {
    "digest": digest,
    "vault": vault_tasks,
    "utils": utils
}

output = {}

for modname, module in modules.items():
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if hasattr(attr, "__wrapped__") and getattr(attr.__wrapped__, "__name__", None) == "task":
            doc = inspect.getdoc(attr)
            if doc:
                output_key = f"{modname}.{attr_name}"
                output[output_key] = doc.splitlines()[0]

with open("docs/task_summaries/cursor_tasks.json", "w") as f:
    json.dump(output, f, indent=2)

print("✅ .cursor-tasks.json updated.")

import subprocess
import datetime
subprocess.run(["git", "add", "docs/task_summaries/cursor_tasks.json"])
version_tag = datetime.datetime.now().strftime("v%Y.%m.%d-%H%M")
subprocess.run(["git", "commit", "-m", f"🔄 Update cursor task summaries ({version_tag})"])

# subprocess.run(["gh", "workflow", "run", "cursor-tasks-update.yml"])

print("🚀 Ready for CI integration or deeper task chaining.")


# Additional file: README.md

with open("README.md", "a+") as readme_file:
    readme_file.seek(0)
    content = readme_file.read()
    appendix = """

## Task Summary Auto-Generation

The script `scripts/generate_cursor_tasks.py` collects task descriptions from decorated Fabric tasks and writes them to `docs/task_summaries/cursor_tasks.json`.

Run it with:

```bash
python scripts/generate_cursor_tasks.py
```

The output file is auto-staged and auto-committed with a versioned timestamp.
"""
    if appendix.strip() not in content:
        readme_file.write(appendix)