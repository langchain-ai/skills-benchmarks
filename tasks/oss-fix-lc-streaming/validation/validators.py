"""Pattern-based validators for oss-fix-lc-streaming task.

Checks for correct patterns indicating fixes from lc_streaming + lc_tools.
Returns (passed: list[str], failed: list[str]).
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    eval_dir=Path(__file__).parent,
    test_script="test_streaming.py",
    module_file="chat_app.py",
)

# List of all validators
VALIDATORS = [
    validate_execution,
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run the main execution validator and return results."""
    return validate_execution(test_dir, outputs)
