"""Testing scaffold for Claude Code skill benchmarks."""

from .runner import run_test, run_with_repetition, TestResult, RepetitionResult
from .capture import extract_events, did_read, did_create, tool_count
from .setup import setup_test_environment, cleanup_test_environment, copy_test_data
from .templates import build_skill, write_skill, setup_test_context

__all__ = [
    'run_test', 'run_with_repetition', 'TestResult', 'RepetitionResult',
    'extract_events', 'did_read', 'did_create', 'tool_count',
    'setup_test_environment', 'cleanup_test_environment', 'copy_test_data',
    'build_skill', 'write_skill', 'setup_test_context',
]
