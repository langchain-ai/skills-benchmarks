"""Python-specific scaffold components.

- schema.py: NoiseTask, Treatment
- validation.py: Validators
- utils.py: Docker wrappers, helpers
- logging.py: Output parsing, experiment logging
"""

from .logging import (
    ExperimentLogger,
    ReportColumn,
    TreatmentResult,
    bool_column,
    default_columns,
    extract_events,
    parse_output,
    quality_column,
    save_events,
    save_raw,
    save_report,
    strip_ansi,
)
from .schema import NoiseTask, Treatment
from .utils import (
    build_docker_image,
    check_claude_available,
    check_docker_available,
    evaluate_with_schema,
    get_eval_model,
    get_field,
    get_nested_field,
    normalize_score,
    read_json_file,
    retry_with_backoff,
    run_claude_in_docker,
    run_in_docker,
    run_node_in_docker,
    run_python_in_docker,
    run_shell,
)
from .validation import (
    MetricsCollector,
    NoiseTaskValidator,
    OutputQualityValidator,
    PythonFileValidator,
    SkillInvokedValidator,
    Validator,
)

__all__ = [
    # Schema
    "NoiseTask",
    "Treatment",
    # Validation
    "Validator",
    "SkillInvokedValidator",
    "PythonFileValidator",
    "NoiseTaskValidator",
    "MetricsCollector",
    "OutputQualityValidator",
    # Utils
    "run_shell",
    "check_docker_available",
    "check_claude_available",
    "build_docker_image",
    "run_in_docker",
    "run_python_in_docker",
    "run_node_in_docker",
    "run_claude_in_docker",
    "retry_with_backoff",
    "read_json_file",
    "get_field",
    "get_nested_field",
    "normalize_score",
    "get_eval_model",
    "evaluate_with_schema",
    # Logging
    "parse_output",
    "extract_events",
    "strip_ansi",
    "ExperimentLogger",
    "TreatmentResult",
    "save_events",
    "save_raw",
    "save_report",
    "ReportColumn",
    "bool_column",
    "quality_column",
    "default_columns",
]
