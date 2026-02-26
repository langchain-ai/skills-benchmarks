"""Validators for ls-multiskill-basic task.

Tests trajectory dataset creation from LangSmith traces.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    eval_dir=Path(__file__).parent,
    test_script="test_dataset.py",
    module_file="trajectory_dataset.json",
    data_dir=Path(__file__).parent.parent / "data",
)

VALIDATORS = [validate_execution]
