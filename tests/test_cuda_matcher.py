from pathlib import Path

import pytest

from app.core.cuda_matcher import choose
from app.core.detector import GpuInfo


TABLE = str(Path("app/data/cuda_torch_map.json"))


def gpu(cuda):
    return GpuInfo("NVIDIA", "550.78", 8192, cuda)


def test_choose_cu124_for_cuda_12_6():
    plan = choose(gpu("12.6"), TABLE)

    assert plan.mode == "gpu"
    assert plan.cuda_tag == "cu124"
    assert plan.spec[0] == "torch==2.5.1+cu124"


def test_choose_cu124_for_cuda_12_4():
    plan = choose(gpu("12.4"), TABLE)

    assert plan.cuda_tag == "cu124"
    assert plan.index_url == "https://download.pytorch.org/whl/cu124"
    assert plan.spec[0] == "torch==2.5.1+cu124"


def test_choose_cu121_for_cuda_12_1():
    assert choose(gpu("12.1"), TABLE).cuda_tag == "cu121"


def test_choose_cu118_for_cuda_11_8():
    assert choose(gpu("11.8"), TABLE).cuda_tag == "cu118"


def test_choose_falls_back_to_cpu_for_too_old_cuda():
    assert choose(gpu("10.2"), TABLE).mode == "cpu"


def test_choose_cpu_without_gpu():
    plan = choose(None, TABLE)

    assert plan.mode == "cpu"
    assert plan.cuda_tag is None
    assert plan.extra_index_url == "https://download.pytorch.org/whl/cpu"


def test_choose_rejects_bad_cuda_value():
    with pytest.raises(ValueError, match="Invalid CUDA version"):
        choose(gpu("bad"), TABLE)
