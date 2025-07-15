from invoke import task, Collection

ns = Collection("sign_pulse")

@task
def sign_all(c):
    print("🔏 Signing all pulses... (placeholder implementation)")

ns.add_task(sign_all, name="all")

__all__ = ["ns"]