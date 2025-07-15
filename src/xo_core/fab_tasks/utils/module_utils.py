from dataclasses import dataclass
from typing import Optional

@dataclass
class ModuleConfig:
    path: str
    name: str
    alias: Optional[str] = None
    required: bool = False
    hidden: bool = False
    category: str = "general"
    description: Optional[str] = None

    @property
    def module_path(self):
        """Return full Python path to the module."""
        return self.path or self.name

def register_modules(ns, configs, verbose=False):
    from xo_core.fab_tasks.dynamic_loader import DynamicTaskLoader
    loader = DynamicTaskLoader(verbose=verbose)
    return loader.load_modules(configs, ns)

from invoke import Collection

ns = Collection()