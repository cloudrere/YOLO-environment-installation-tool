from __future__ import annotations

from app.core.state import InstallState


def resume_summary(state: InstallState) -> str:
    env_name = state.config.get("env_name", "yolo-env")
    last_step = state.finished_steps[-1] if state.finished_steps else "nothing"
    message = f"Previous install for {env_name} finished step {last_step}. You can continue from the next step."
    if state.last_error:
        message += f" Last error: {state.last_error}"
    return message

