import os
import importlib.util
from pathlib import Path
from invoke import Collection

FAB_TASKS_DIR = Path("src/xo_core/fab_tasks")
OUTPUT_DIR = Path(".fab-docs")
OUTPUT_DIR.mkdir(exist_ok=True)

def discover_task_modules(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                yield Path(root) / file

def extract_tasks(module_path):
    try:
        module_name = module_path.with_suffix("").as_posix().replace("/", ".")
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ns = getattr(module, "ns", None)
        if isinstance(ns, Collection):
            return ns
    except Exception:
        pass
    return None

def generate_docs():
    for module_file in discover_task_modules(FAB_TASKS_DIR):
        ns = extract_tasks(module_file)
        if ns:
            lines = [f"# `{module_file.name}` Tasks\n"]
            for task_name in ns.task_names:
                task = ns[task_name]
                lines.append(f"## `{task_name}`\n{task.__doc__ or 'No docstring provided.'}")
            doc_file = OUTPUT_DIR / f"{module_file.stem}.md"
            with doc_file.open("w") as f:
                f.write("\n\n".join(lines))

if __name__ == "__main__":
    generate_docs()
    print("✅ Fabric docs generated in .fab-docs/")
