"""Validators for lc-basic-noise task.

Tests skill retention when distracted by noise tasks.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    validation_dir=Path(__file__).parent,
    test_script="test_agents.py",
    target_artifacts=["sql_agent_1.py", "search_agent.py"],
)

VALIDATORS = [validate_execution]
