from __future__ import annotations

import json
from pathlib import Path

from app.core.errors import InstallError
from app.core.pip_installer import pip_install
from app.utils.paths import resource_path
from app.utils.runner import run


PREDOWNLOAD_SCRIPT = """
import sys
from ultralytics import YOLO, NAS, RTDETR, SAM, FastSAM
name = sys.argv[1]
cls = YOLO
low = name.lower()
if low.startswith('yolo_nas'):
    cls = NAS
elif low.startswith('rtdetr'):
    cls = RTDETR
elif low.startswith('sam'):
    cls = SAM
elif low.startswith('fastsam'):
    cls = FastSAM
cls(name)
print('OK', name)
""".strip()

SMOKE_SCRIPT = """
import sys
from ultralytics import YOLO
model = YOLO(sys.argv[1])
results = model(sys.argv[2])
results[0].save(filename=sys.argv[3])
print('OK', sys.argv[3])
""".strip()


def install_ultralytics(python_exe: str, on_line=None) -> None:
    pip_install(
        python_exe,
        ["ultralytics>=8.3,<9"],
        index_url="https://pypi.tuna.tsinghua.edu.cn/simple",
        on_line=on_line,
    )


def predownload_weights(
    python_exe: str,
    weights: list[str],
    weight_dir: str,
    on_line=None,
) -> dict[str, str]:
    Path(weight_dir).mkdir(parents=True, exist_ok=True)
    out: dict[str, str] = {}
    for weight in weights:
        result = run(
            [python_exe, "-c", PREDOWNLOAD_SCRIPT, weight],
            env={"YOLO_CONFIG_DIR": weight_dir},
            on_line=on_line,
        )
        if result.returncode != 0:
            raise InstallError(f"weight download failed: {weight}")
        out[weight] = str(Path(weight_dir) / weight)
    return out


def smoke_test(python_exe: str, weight: str, image_path: str, out_path: str) -> bool:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    result = run([python_exe, "-c", SMOKE_SCRIPT, weight, image_path, out_path])
    return result.returncode == 0


def weights_from_model_ids(model_ids: list[str], data_path: str = "app/data/yolo_models.json") -> list[str]:
    path = Path(data_path)
    if not path.is_absolute():
        path = resource_path(data_path)
    table = json.loads(path.read_text(encoding="utf-8"))
    selected: list[str] = []
    for requested in model_ids:
        model_id, _, variant = requested.partition(":")
        for group in table["groups"]:
            for item in group["items"]:
                if item["id"] != model_id:
                    continue
                if "weights" in item:
                    selected.extend(item["weights"])
                    break
                scale = variant or item.get("scales", ["n"])[0]
                suffix = item.get("suffix", "")
                selected.append(f"{model_id}{scale}{suffix}.pt")
                break
    return selected
