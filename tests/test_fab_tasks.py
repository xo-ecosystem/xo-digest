import pytest
from invoke import Context

from src.xo_core.fab_tasks import tasks as validate_tasks


def test_validate_tasks_runs_without_error(monkeypatch):
    class MockContext(Context):
        def run(self, *args, **kwargs):
            return type("Result", (), {"stdout": "ok", "ok": True})()

    c = MockContext()
    try:
        validate_tasks["validate-tasks"](c)
    except Exception as e:
        pytest.fail(f"validate_tasks['validate-tasks'] raised an exception: {e}")


def test_validate_tasks_with_mocked_context(monkeypatch):
    class MockContext(Context):
        def run(self, *args, **kwargs):
            return type("Result", (), {"stdout": "ok", "ok": True})()

    monkeypatch.setattr("invoke.Context", MockContext)
    c = MockContext()
    result = validate_tasks["validate-tasks"](c)
    assert result is None


if __name__ == "__main__":
    import os
    import webbrowser
    from datetime import datetime

    report_dir = "reports"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(report_dir, f"test_report_{timestamp}.html")

    os.makedirs(report_dir, exist_ok=True)
    os.system(f"pytest tests/ --html={report_path} --self-contained-html")
    webbrowser.open(f"file://{os.path.abspath(report_path)}")
