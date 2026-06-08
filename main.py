from __future__ import annotations

import argparse
import json

from app.core.cuda_matcher import choose
from app.core.detector import detect_all
from app.core.pipeline import Pipeline
from app.core.ultralytics_setup import weights_from_model_ids


def main() -> int:
    parser = argparse.ArgumentParser(description="YOLO installer M1 CLI")
    parser.add_argument("--dry-run", action="store_true", help="Run pipeline callbacks without installing")
    parser.add_argument("--models", nargs="*", default=["yolov8:n"], help="Model specs such as yolov8:n")
    args = parser.parse_args()

    snapshot = detect_all()
    plan = choose(snapshot.gpu, "app/data/cuda_torch_map.json")
    print(json.dumps({"snapshot": snapshot.__dict__, "torch_plan": plan.__dict__}, ensure_ascii=False, default=str, indent=2))

    if args.dry_run:
        events: list[str] = []
        config = {
            "python_exe": "python",
            "conda_exe": "conda",
            "weights": weights_from_model_ids(args.models),
            "torch_plan": plan.__dict__,
            "install_jupyter": False,
            "make_shortcut": False,
        }
        pipe = Pipeline(config, events.append, lambda step, status: events.append(f"{step}:{status}"), lambda ok, msg: events.append(f"done:{ok}:{msg}"))
        for step in Pipeline.STEPS:
            setattr(pipe, f"_do_{step}", lambda: None)
        pipe.run()
        print("\n".join(events))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
