"""Testing scaffold for Claude Code skill benchmarks."""

from .runner import (
    run_test, TestResult,
    check_docker_available, build_docker_image, run_in_docker, run_python_in_docker,
    extract_events, parse_output, save_events,
)
from .setup import (
    verify_environment,
    setup_test_environment, cleanup_test_environment,
    build_skill, write_skill, setup_test_context,
    cleanup_test_files, cleanup_langsmith_assets,
)
from .framework import (
    Treatment, Validator,
    SkillInvokedValidator, PythonFileValidator, NoiseTaskValidator,
    MetricsCollector, OutputQualityValidator,
    NOISE_TASKS, get_noise_prompt, get_noise_output, get_noise_skill_content,
    langchain_skill_validator, python_files_validator, metrics_collector,
)
from .model import (
    EVAL_MODEL, get_eval_model, evaluate_output, evaluate_with_json,
)

__all__ = [
    # Runner (includes Docker and event parsing)
    'run_test', 'TestResult',
    'build_docker_image', 'run_in_docker', 'run_python_in_docker',
    'extract_events', 'parse_output', 'save_events',
    # Setup
    'verify_environment',
    'setup_test_environment', 'cleanup_test_environment',
    'build_skill', 'write_skill', 'setup_test_context',
    'cleanup_test_files', 'cleanup_langsmith_assets',
    # Experiment
    'Treatment', 'Validator',
    'SkillInvokedValidator', 'PythonFileValidator', 'NoiseTaskValidator',
    'MetricsCollector', 'OutputQualityValidator',
    'NOISE_TASKS', 'get_noise_prompt', 'get_noise_output', 'get_noise_skill_content',
    'langchain_skill_validator', 'python_files_validator', 'metrics_collector',
    # Model
    'EVAL_MODEL', 'get_eval_model', 'evaluate_output', 'evaluate_with_json',
]
