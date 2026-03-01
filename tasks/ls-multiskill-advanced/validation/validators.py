"""Validators for ls-multiskill-advanced task.

Tests trajectory dataset creation and Python evaluator from LangSmith traces.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    validation_dir=Path(__file__).parent,
    test_script="test_advanced.py",
    target_artifacts="trajectory_dataset.json",
    data_dir=Path(__file__).parent.parent / "data",
)

VALIDATORS = [validate_execution]
