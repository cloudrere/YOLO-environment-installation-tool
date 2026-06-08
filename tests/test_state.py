from app.core import state
from app.core.state import InstallState


def test_save_and_load_state(tmp_path, monkeypatch):
    monkeypatch.setattr(state, "STATE_PATH", tmp_path / "state.json")
    expected = InstallState("2026-06-08T00:00:00", ["detect"], {"env_name": "yolo-env"})

    state.save(expected)

    assert state.load() == expected


def test_load_returns_none_when_state_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(state, "STATE_PATH", tmp_path / "missing.json")

    assert state.load() is None


def test_load_returns_none_for_corrupt_state(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    path.write_text("{bad", encoding="utf-8")
    monkeypatch.setattr(state, "STATE_PATH", path)

    assert state.load() is None


def test_clear_removes_state_file(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(state, "STATE_PATH", path)

    state.clear()

    assert not path.exists()
