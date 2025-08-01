from invoke import task
import os
import shutil


@task
def site(c, build=False, dev=False, deploy=False):
    """
    Build, dev, or serve the foundation site.
    """
    if build:
        os.system("npm run build:foundation")
    if dev:
        os.system("npm run dev:foundation")
    if not build and not dev and not deploy:
        os.system("npm run serve:foundation")

    if build or dev or deploy:
        source = "public/21xo"
        target = "public/foundation"

        if os.path.exists(target):
            shutil.rmtree(target)
        shutil.copytree(source, target)
        print(f"✅ Deployed landing site from {source} to {target}")


from invoke import Collection

ns = Collection("foundation")
ns.add_task(site, "site")
