"""Validators for lc-basic task.

Tests SQL agent creation with modern LangChain patterns.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    validation_dir=Path(__file__).parent,
    test_script="test_sql_agent.py",
    target_artifacts="sql_agent_1.py",
)

VALIDATORS = [validate_execution]
