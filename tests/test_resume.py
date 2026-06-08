from app.core.resume import resume_summary
from app.core.state import InstallState


def test_resume_summary_describes_last_finished_step():
    state = InstallState(
        started_at="2026-06-08T15:00:00",
        finished_steps=["detect", "conda", "env"],
        config={"env_name": "yolo-env"},
    )

    summary = resume_summary(state)

    assert "yolo-env" in summary
    assert "env" in summary
    assert "continue" in summary.lower()


def test_resume_summary_mentions_error_when_present():
    state = InstallState(
        started_at="2026-06-08T15:00:00",
        finished_steps=["detect"],
        config={"env_name": "demo"},
        last_error="network failed",
    )

    assert "network failed" in resume_summary(state)
