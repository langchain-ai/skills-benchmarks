"""Harbor migration package for skills-benchmarks.

Ships the task converter (scripts/convert_task.py) and the treatment logic: a
treatment is a list of skill refs, and ``materialize_treatment`` renders it into
the agent-agnostic ``skills_dir`` layout Harbor injects via ``--skills`` for any
coding agent (claude-code, codex, langgraph/deepagents, ...). No custom agent is
needed — skill injection is native to Harbor.
"""

from skillbench_harbor.treatments import (
    list_treatments,
    load_treatments,
    materialize_skills,
    materialize_treatment,
)

__version__ = "0.0.1"

__all__ = [
    "list_treatments",
    "load_treatments",
    "materialize_skills",
    "materialize_treatment",
]
