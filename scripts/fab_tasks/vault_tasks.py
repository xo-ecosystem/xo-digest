from invoke import Collection, task


@task(help={"slug": "Name of the file to sign (without extension)"})
def sign(c, slug):
    print(f"🔐 Signing vault file: {slug}")
    # Insert logic here


@task
def sign_all(c):
    print("🧾 Signing all .coin.yml and .mdx files in vault/")
    # Insert logic here


@task
def explorer_deploy(c):
    print("🚀 Deploying vault explorer")
    # Insert logic here


ns = Collection("vault")
ns.add_task(sign)
ns.add_task(sign_all, name="sign-all")
ns.add_task(explorer_deploy, name="explorer-deploy")
