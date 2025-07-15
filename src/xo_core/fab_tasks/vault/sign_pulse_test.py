from invoke import task, Collection

ns = Collection("sign_pulse_test")

@task
def test_sign(c):
    """🧪 Test signing functionality."""
    print("🧪 Testing sign pulse functionality... (placeholder)")

ns.add_task(test_sign, name="test")

__all__ = ["ns"]