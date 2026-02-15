"""Python-specific scaffold components.

- schema.py: NoiseTask, Treatment
- validation.py: Validators
- utils.py: Docker wrappers, helpers
- logging.py: Output parsing, experiment logging
"""

from .schema import NoiseTask, Treatment
from .validation import (
    Validator, SkillInvokedValidator, PythonFileValidator,
    NoiseTaskValidator, MetricsCollector, OutputQualityValidator,
)
from .utils import (
    run_shell, check_docker_available, check_claude_available,
    build_docker_image, run_in_docker, run_python_in_docker, run_claude_in_docker,
    retry_with_backoff, read_json_file, get_field, get_nested_field,
    normalize_score, extract_score, get_eval_model, evaluate_with_schema,
)
from .logging import (
    parse_output, extract_events, strip_ansi,
    ExperimentLogger, TreatmentResult,
    save_events, save_raw, save_report,
    ReportColumn, bool_column, quality_column, default_columns,
)

__all__ = [
    # Schema
    'NoiseTask', 'Treatment',
    # Validation
    'Validator', 'SkillInvokedValidator', 'PythonFileValidator',
    'NoiseTaskValidator', 'MetricsCollector', 'OutputQualityValidator',
    # Utils
    'run_shell', 'check_docker_available', 'check_claude_available',
    'build_docker_image', 'run_in_docker', 'run_python_in_docker', 'run_claude_in_docker',
    'retry_with_backoff', 'read_json_file', 'get_field', 'get_nested_field',
    'normalize_score', 'extract_score', 'get_eval_model', 'evaluate_with_schema',
    # Logging
    'parse_output', 'extract_events', 'strip_ansi',
    'ExperimentLogger', 'TreatmentResult',
    'save_events', 'save_raw', 'save_report',
    'ReportColumn', 'bool_column', 'quality_column', 'default_columns',
]
