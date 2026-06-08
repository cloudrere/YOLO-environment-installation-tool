from app.core import pipeline, state


def test_pipeline_runs_steps_in_order_and_saves_state(monkeypatch, tmp_path):
    saved = []
    events = []
    monkeypatch.setattr(state, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(state, "save", lambda snapshot: saved.append(snapshot))

    def step(name):
        return lambda self: events.append(name)

    for name in pipeline.Pipeline.STEPS:
        monkeypatch.setattr(pipeline.Pipeline, f"_do_{name}", step(name))

    done = []
    pipe = pipeline.Pipeline({"env_name": "demo"}, events.append, lambda s, st: events.append(f"{s}:{st}"), lambda ok, msg: done.append((ok, msg)))

    pipe.run()

    assert done == [(True, "")]
    assert [item for item in events if item in pipeline.Pipeline.STEPS] == pipeline.Pipeline.STEPS
    assert [snapshot.finished_steps[-1] for snapshot in saved] == pipeline.Pipeline.STEPS


def test_pipeline_cancel_stops_before_next_step(monkeypatch):
    events = []

    def cancel_on_detect(self):
        events.append("detect")
        self.cancel()

    monkeypatch.setattr(pipeline.Pipeline, "_do_detect", cancel_on_detect)
    for name in pipeline.Pipeline.STEPS[1:]:
        monkeypatch.setattr(pipeline.Pipeline, f"_do_{name}", lambda self: events.append("unexpected"))

    done = []
    pipe = pipeline.Pipeline({}, events.append, lambda s, st: events.append(f"{s}:{st}"), lambda ok, msg: done.append((ok, msg)))

    pipe.run()

    assert "unexpected" not in events
    assert done == [(False, "canceled")]


def test_pipeline_reports_failed_step(monkeypatch):
    events = []

    def fail(self):
        raise RuntimeError("boom")

    monkeypatch.setattr(pipeline.Pipeline, "_do_detect", fail)

    done = []
    pipe = pipeline.Pipeline({}, events.append, lambda s, st: events.append(f"{s}:{st}"), lambda ok, msg: done.append((ok, msg)))

    pipe.run()

    assert "detect:fail" in events
    assert done == [(False, "boom")]
