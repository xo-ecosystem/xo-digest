from invoke import Collection, task

from fab_tasks import tunnel_tasks


@task
def tunnel_deploy(c, service, port, subdomain):
    """
    🚇 Deploy a tunnel for the given service/port/subdomain.
    """
    print(f"Deploying tunnel for {service} on port {port} with subdomain {subdomain}.")
    # your tunnel logic here


ns = Collection()
ns.add_task(tunnel_deploy, name="tunnel-deploy")
