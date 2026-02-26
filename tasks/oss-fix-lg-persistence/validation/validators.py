"""Execution-based validators for oss-fix-lg-persistence task.

Each validator runs the actual code and checks behavior, not just patterns.
Returns (passed: list[str], failed: list[str]).
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    eval_dir=Path(__file__).parent,
    test_script="test_persistence.py",
    module_file="broken_agent.py",
)

VALIDATORS = [
    validate_execution,
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run the main execution validator and return results."""
    return validate_execution(test_dir, outputs)
