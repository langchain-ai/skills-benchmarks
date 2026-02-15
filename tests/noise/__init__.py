"""Noise task definitions for distractor experiments.

Tasks are defined in tasks.json. Use get_task() or get_tasks() to access them.

Example:
    from tests.noise import get_tasks
    from scaffold import Treatment

    Treatment(
        description="With noise",
        noise_tasks=get_tasks(["docker-patterns", "react-components"]),
    )
"""

import json
from pathlib import Path
from typing import List

from scaffold import NoiseTask

_TASKS_FILE = Path(__file__).parent / "tasks.json"
_cache = None


def _load() -> dict:
    global _cache
    if _cache is None:
        _cache = json.loads(_TASKS_FILE.read_text())
    return _cache


def get_task(name: str) -> NoiseTask:
    """Get a noise task by name."""
    data = _load()[name]
    return NoiseTask(prompt=data["prompt"], deliverables=[data["output"]])


def get_tasks(names: List[str]) -> List[NoiseTask]:
    """Get multiple noise tasks by name."""
    return [get_task(n) for n in names]
