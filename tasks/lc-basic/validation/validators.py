"""Validators for lc-basic task.

Tests SQL agent creation with modern LangChain patterns.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    eval_dir=Path(__file__).parent,
    test_script="test_sql_agent.py",
    module_file="sql_agent_1.py",
)

VALIDATORS = [validate_execution]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    return validate_execution(test_dir, outputs)
