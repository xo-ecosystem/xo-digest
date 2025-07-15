from invoke import Collection, task

from xo_core.fab_tasks import ci, core_tasks, digest_tasks, pulse_namespace, summary
from xo_core.fab_tasks import validate_tasks as validate_module
from xo_core.fab_tasks import vault

ns = Collection("xo")

ci_ns = Collection("ci")
ci_ns.add_task(ci.publish, name="publish")
ns.add_collection(ci_ns, name="ci")

digest_ns = Collection("digest")
digest_ns.add_task(digest_tasks.digest_push, name="push")

vault_ns = Collection("vault")
vault_ns.add_task(vault.sign_all, name="sign-all")
vault_ns.add_task(vault.verify_all, name="verify-all")
vault_ns.add_collection(digest_ns, name="digest")

ns.add_collection(vault_ns, name="vault")
ns.add_collection(pulse_namespace.pulse_ns, name="pulse")


core_ns = Collection("core")
core_ns.add_collection(core_tasks, name="core")
ns.add_collection(core_ns)

validate_ns = Collection("validate")
validate_ns.add_task(validate_module.validate_tasks, name="validate")
ns.add_collection(validate_ns)


# Dummy default task to satisfy Fabric validation
@task
def default(ctx):
    """Default no-op task to satisfy Fabric validation."""
    pass


ns.add_task(default, name="default")

ns.add_collection(summary.summary_ns, name="summary")

namespace = ns
