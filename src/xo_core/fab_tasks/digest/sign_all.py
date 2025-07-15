from invoke import task

@task
def sign_all(c):
    """
    Dummy sign_all task for digest namespace.
    """
    print("✅ digest.sign_all placeholder executed.")


from invoke import Collection
ns = Collection("sign_all")
ns.add_task(sign_all, name="sign_all")