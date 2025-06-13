import pytest
from invoke import Context
from fab_tasks import validate_tasks

def test_validate_tasks_runs_without_error():
    c = Context()
    try:
        validate_tasks.tasks(c)
    except Exception as e:
        pytest.fail(f"validate_tasks.tasks raised an exception: {e}")

def test_validate_tasks_with_mocked_context(monkeypatch):
    class MockContext:
        def run(self, *args, **kwargs):
            return type("Result", (), {"stdout": "ok", "ok": True})()

    monkeypatch.setattr(validate_tasks, "Context", MockContext)
    c = MockContext()
    try:
        validate_tasks.tasks(c)
    except Exception as e:
        pytest.fail(f"Mocked validate_tasks.tasks raised an exception: {e}")
