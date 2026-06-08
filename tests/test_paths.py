import sys

from app.utils.paths import resource_path


def test_resource_path_uses_pyinstaller_meipass(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    assert resource_path("app/data/cuda_torch_map.json") == tmp_path / "app/data/cuda_torch_map.json"


def test_resource_path_uses_project_root_without_meipass(monkeypatch):
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    path = resource_path("app/data/cuda_torch_map.json")

    assert path.name == "cuda_torch_map.json"
    assert path.exists()
