"""Function-based validation utilities for benchmark tasks.

This package provides composable validation functions organized by domain:
- core: Basic utilities (file exists, pattern matching, compose)
- tracing: Python/TypeScript LangSmith tracing validation + API verification
- docker: Docker-based code execution validation
- langsmith: LangSmith API client helpers
- dataset: Dataset structure and trajectory validation
- evaluator: Evaluator validation (syntax, patterns, logic, upload)
- scripts: Skill script usage tracking

Each validator function returns (passed: list[str], failed: list[str]).

Usage:
    from scaffold.python.validation import (
        validate_python_tracing,
        validate_typescript_tracing,
        validate_code_execution,
    )

    # In task validators.py
    def validate_tracing(test_dir: Path, outputs: dict):
        passed, failed = [], []
        py_p, py_f = validate_python_tracing(test_dir, "backend/agent.py")
        passed.extend(py_p)
        failed.extend(py_f)
        return passed, failed
"""

from scaffold.python.validation.core import (
    NOISE_TASK_DELIVERABLES,
    NOISE_TASK_PROMPTS,
    ValidatorFn,
    compose_validators,
    get_noise_task_prompts,
    run_validators,
    validate_file_exists,
    validate_no_pattern,
    validate_noise_outputs,
    validate_pattern,
    validate_skill_invoked,
)
from scaffold.python.validation.dataset import (
    extract_examples,
    get_field,
    get_nested_field,
    validate_dataset_structure,
    validate_dataset_upload,
    validate_trajectory_accuracy,
)
from scaffold.python.validation.docker import (
    validate_code_execution,
    validate_python_execution,
    validate_typescript_execution,
)
from scaffold.python.validation.evaluator import (
    find_evaluator_function,
    validate_evaluator_exists,
    validate_evaluator_logic,
    validate_evaluator_patterns,
    validate_evaluator_syntax,
    validate_evaluator_upload,
)
from scaffold.python.validation.langsmith import (
    get_langsmith_client,
    safe_api_call,
)
from scaffold.python.validation.scripts import validate_skill_scripts
from scaffold.python.validation.tracing import (
    validate_langsmith_trace,
    validate_language_syntax,
    validate_python_tracing,
    validate_typescript_tracing,
)


__all__ = [
    # Core
    "ValidatorFn",
    "compose_validators",
    "run_validators",
    "validate_file_exists",
    "validate_pattern",
    "validate_no_pattern",
    "validate_skill_invoked",
    "validate_noise_outputs",
    "get_noise_task_prompts",
    "NOISE_TASK_DELIVERABLES",
    "NOISE_TASK_PROMPTS",
    # Tracing
    "validate_python_tracing",
    "validate_typescript_tracing",
    "validate_language_syntax",
    "validate_langsmith_trace",
    # Docker
    "validate_code_execution",
    "validate_python_execution",
    "validate_typescript_execution",
    # LangSmith
    "get_langsmith_client",
    "safe_api_call",
    # Dataset
    "extract_examples",
    "get_field",
    "get_nested_field",
    "validate_dataset_structure",
    "validate_dataset_upload",
    "validate_trajectory_accuracy",
    # Evaluator
    "find_evaluator_function",
    "validate_evaluator_exists",
    "validate_evaluator_syntax",
    "validate_evaluator_patterns",
    "validate_evaluator_logic",
    "validate_evaluator_upload",
    # Scripts
    "validate_skill_scripts",
]
