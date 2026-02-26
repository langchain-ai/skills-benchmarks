"""Validators for lc-framework-choice task.

Tests whether Claude picks the right framework for each component.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator

validate_execution = make_execution_validator(
    eval_dir=Path(__file__).parent,
    test_script="test_framework.py",
    module_file=[
        "qa_agent.py",
        "approval_pipeline.py",
        "middleware_agent.py",
        "research_assistant.py",
        "personal_assistant.py",
    ],
)

VALIDATORS = [validate_execution]
