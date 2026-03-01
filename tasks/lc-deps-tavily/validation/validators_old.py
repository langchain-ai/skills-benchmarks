"""Validators for lc-deps-tavily task.

Tests fixing broken Tavily dependency imports.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    validation_dir=Path(__file__).parent,
    test_script="test_tavily_agent.py",
    target_artifacts="agent.py",
)

VALIDATORS = [validate_execution]
