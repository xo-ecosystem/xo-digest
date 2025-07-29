from invoke import Collection

# Import local modules
from src.xo_core.fab_tasks.dns_check_21xo import check_dns
from src.xo_core.fab_tasks.deploy import test_deploy

ns = Collection()
ns.add_task(check_dns, "dns.check")
ns.add_task(test_deploy, "deploy.test")
