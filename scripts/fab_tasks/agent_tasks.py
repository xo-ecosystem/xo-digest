from invoke import Collection, task


@task(help={"persona": "Name of the persona to deploy"})
def deploy_persona(c, persona):
    print(f"🧠 Deploying agent persona: {persona}")
    # Insert logic here


@task
def reload_all(c):
    print("🔄 Reloading all agent personas...")
    # Insert logic here


ns = Collection("agent")
ns.add_task(deploy_persona, name="deploy-persona")
ns.add_task(reload_all, name="reload-all")
