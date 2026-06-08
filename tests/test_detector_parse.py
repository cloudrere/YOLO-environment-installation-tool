from pathlib import Path

from app.core.detector import CondaInfo, GpuInfo, parse_conda_env_list, parse_nvidia_smi


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_nvidia_smi_v550():
    gpu = parse_nvidia_smi((FIXTURES / "nvidia_smi_550.txt").read_text(encoding="utf-8"))

    assert gpu == GpuInfo(
        name="NVIDIA GeForce RTX 4070",
        driver="550.78",
        memory_mib=12282,
        cuda_runtime_max="12.4",
    )


def test_parse_nvidia_smi_legacy_driver():
    gpu = parse_nvidia_smi((FIXTURES / "nvidia_smi_legacy.txt").read_text(encoding="utf-8"))

    assert gpu.name == "NVIDIA GeForce GTX 1060"
    assert gpu.cuda_runtime_max == "11.4"
    assert gpu.memory_mib == 6144


def test_parse_nvidia_smi_returns_none_without_cuda_table():
    assert parse_nvidia_smi((FIXTURES / "nvidia_smi_no_gpu.txt").read_text(encoding="utf-8")) is None


def test_parse_conda_env_list_ignores_comments_and_paths():
    envs = parse_conda_env_list((FIXTURES / "conda_env_list.txt").read_text(encoding="utf-8"))

    assert envs == ["base", "ultralytics", "yolo"]


def test_conda_info_is_plain_dataclass():
    assert CondaInfo(path=None, version=None, envs=[]).envs == []
