from __future__ import annotations

import argparse
import json
import sys

from app.core.cuda_matcher import choose
from app.core.detector import detect_all
from app.core.pipeline import Pipeline


def run_gui(*, dry_run: bool) -> int:
    from PyQt6.QtWidgets import QApplication

    from app.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(dry_run=dry_run)
    window.show()
    return app.exec()


def main() -> int:
    parser = argparse.ArgumentParser(description="YOLO installer M1 CLI")
    parser.add_argument("--gui", action="store_true", help="Launch the PyQt6 desktop interface")
    parser.add_argument("--dry-run", action="store_true", help="Run pipeline callbacks without installing")
    args = parser.parse_args()

    if args.gui or len(sys.argv) == 1:
        return run_gui(dry_run=args.dry_run)

    snapshot = detect_all()
    plan = choose(snapshot.gpu, "app/data/cuda_torch_map.json")
    print(json.dumps({"snapshot": snapshot.__dict__, "torch_plan": plan.__dict__}, ensure_ascii=False, default=str, indent=2))

    if args.dry_run:
        events: list[str] = []
        config = {
            "python_exe": "python",
            "conda_exe": "conda",
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
