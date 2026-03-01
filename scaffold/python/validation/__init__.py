"""Validation helpers for test scripts.

These are helper functions used by test scripts running inside Docker.
They are NOT standalone validators — use make_execution_validator to
wire test scripts into the benchmark infrastructure.

Modules:
- core: File checks, pattern matching, skill tracking, noise outputs
- tracing: LangSmith tracing pattern checks + API verification
- docker: Code execution checks
- dataset: Dataset structure, upload, and accuracy checks
- evaluator: Evaluator file checks and logic execution
- scripts: Skill script usage tracking

Each helper returns (passed: list[str], failed: list[str]).
"""

from scaffold.python.utils import get_langsmith_client, safe_api_call
from scaffold.python.validation.core import (
    NOISE_TASK_DELIVERABLES,
    NOISE_TASK_PROMPTS,
    ValidatorFn,
    check_file_exists,
    check_no_pattern,
    check_noise_outputs,
    check_pattern,
    check_skill_invoked,
    check_starter_skill_first,
    compose_validators,
    get_noise_task_prompts,
    run_validators,
)
from scaffold.python.validation.dataset import (
    check_dataset_structure,
    check_dataset_upload,
    check_trajectory_accuracy,
    extract_examples,
)
from scaffold.python.validation.docker import (
    check_code_execution,
    check_python_execution,
    check_typescript_execution,
)
from scaffold.python.validation.evaluator import (
    check_evaluator_exists,
    check_evaluator_logic,
    check_evaluator_patterns,
    check_evaluator_syntax,
    check_evaluator_upload,
    find_evaluator_function,
)
from scaffold.python.validation.scripts import check_skill_scripts
from scaffold.python.validation.tracing import (
    check_langsmith_trace,
    check_language_syntax,
    check_python_tracing,
    check_typescript_tracing,
)

__all__ = [
    # Core
    "ValidatorFn",
    "compose_validators",
    "run_validators",
    "check_file_exists",
    "check_pattern",
    "check_no_pattern",
    "check_skill_invoked",
    "check_starter_skill_first",
    "check_noise_outputs",
    "get_noise_task_prompts",
    "NOISE_TASK_DELIVERABLES",
    "NOISE_TASK_PROMPTS",
    # Tracing
    "check_python_tracing",
    "check_typescript_tracing",
    "check_language_syntax",
    "check_langsmith_trace",
    # Docker
    "check_code_execution",
    "check_python_execution",
    "check_typescript_execution",
    # LangSmith
    "get_langsmith_client",
    "safe_api_call",
    # Dataset
    "extract_examples",
    "check_dataset_structure",
    "check_dataset_upload",
    "check_trajectory_accuracy",
    # Evaluator
    "find_evaluator_function",
    "check_evaluator_exists",
    "check_evaluator_syntax",
    "check_evaluator_patterns",
    "check_evaluator_logic",
    "check_evaluator_upload",
    # Scripts
    "check_skill_scripts",
]
