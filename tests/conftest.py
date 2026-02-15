"""Shared pytest fixtures and experiment logging plugin.

Generates rich experiment logs in logs/experiments/ including:
- summary.md: Full markdown report with tables and details
- events/: Parsed events from each test run
- raw/: Raw Claude CLI output
- reports/: Per-run validation reports
- artifacts/: Files Claude generated and their execution output
- metadata.json: Experiment metadata
"""

import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pytest
from dotenv import load_dotenv

from scaffold import run_claude_in_docker, run_python_in_docker, run_shell
from scaffold.python import (
    ExperimentLogger,
    TreatmentResult,
    parse_output,
    extract_events,
    strip_ansi,
    save_events,
    save_raw,
    save_report,
)

PROJECT_ROOT = Path(__file__).parent.parent


# =============================================================================
# EXPERIMENT LOGGING PLUGIN
# =============================================================================

class ExperimentPlugin:
    """Pytest plugin that generates rich experiment logs in logs/experiments/."""

    def __init__(self):
        self.logger: Optional[ExperimentLogger] = None
        self.start_time = None
        self.run_counter: Dict[str, int] = {}  # treatment_name -> repetition count

    def pytest_sessionstart(self, session):
        """Create experiment logger at session start."""
        # Determine experiment name from the test path
        # e.g., tests/langchain_agent/test_guidance.py -> "guidance"
        items = getattr(session, 'items', None)
        if items:
            first_path = str(items[0].fspath) if items else ""
        else:
            first_path = ""

        if "langchain_agent" in first_path:
            if "guidance" in first_path:
                name = "lc_guide"
            elif "claudemd" in first_path:
                name = "lc_claude"
            elif "noise" in first_path:
                name = "lc_noise"
            else:
                name = "lc_agent"
        elif "langsmith_synergy" in first_path:
            if "basic" in first_path:
                name = "ls_basic"
            elif "advanced" in first_path:
                name = "ls_adv"
            else:
                name = "ls_synergy"
        else:
            name = "experiment"

        self.logger = ExperimentLogger(experiment_name=name)
        self.start_time = time.time()

        print(f"\n{'='*60}")
        print(f"EXPERIMENT: {self.logger.experiment_id}")
        print(f"Logging to: {self.logger.base_dir}")
        print(f"{'='*60}\n")

    def get_rep_number(self, treatment_name: str) -> int:
        """Get the next repetition number for a treatment."""
        if treatment_name not in self.run_counter:
            self.run_counter[treatment_name] = 0
        self.run_counter[treatment_name] += 1
        return self.run_counter[treatment_name]

    def pytest_sessionfinish(self, session, exitstatus):
        """Generate and save summary at session end."""
        if self.logger and self.logger.results:
            self.logger.finalize()
            self._print_summary()

    def _print_summary(self):
        """Print summary to console."""
        print(f"\n{'='*80}")
        print("  RESULTS")
        print(f"{'='*80}\n")

        print(f"{'Treatment':<30} {'Checks':<15} {'Turns':<8} {'Duration':<10}")
        print("-" * 80)

        for treatment, runs in self.logger.results.items():
            for r in runs:
                checks_passed = len(r.checks_passed)
                checks_total = checks_passed + len(r.checks_failed)
                check_pct = (checks_passed / checks_total * 100) if checks_total > 0 else 0
                checks_str = f"{checks_passed}/{checks_total} ({check_pct:.0f}%)"
                turns = str(r.turns) if r.turns else "?"
                dur = f"{r.duration:.0f}s" if r.duration else "?"
                print(f"{treatment:<30} {checks_str:<15} {turns:<8} {dur:<10}")

        print("-" * 80)
        total_passed = sum(sum(len(r.checks_passed) for r in runs) for runs in self.logger.results.values())
        total_checks = sum(sum(len(r.checks_passed) + len(r.checks_failed) for r in runs) for runs in self.logger.results.values())
        if total_checks:
            print(f"Total: {total_passed}/{total_checks} checks passed ({total_passed/total_checks*100:.1f}%)")
        print(f"{'='*80}")


# Global plugin instance (set during pytest_configure)
_plugin: Optional[ExperimentPlugin] = None


def pytest_configure(config):
    """Register experiment plugin."""
    global _plugin
    _plugin = ExperimentPlugin()
    config.pluginmanager.register(_plugin, "experiment_plugin")


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def project_root():
    """Project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def worker_id(request):
    """Get pytest-xdist worker ID, or 'master' if not using xdist."""
    if hasattr(request.config, "workerinput"):
        return request.config.workerinput["workerid"]
    return "master"


@pytest.fixture(scope="session")
def verify_environment(project_root):
    """Verify Docker, Claude CLI, and API keys are available."""
    load_dotenv(project_root / ".env")

    # Check Docker
    result = run_shell("docker.sh", "check", check=False)
    if result.returncode != 0:
        pytest.skip("Docker not available")

    # Check API keys
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set")
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    # Check Claude CLI
    result = subprocess.run(["which", "claude"], capture_output=True)
    if result.returncode != 0:
        pytest.skip("Claude CLI not available")


@pytest.fixture
def test_dir(tmp_path):
    """Create isolated test directory (pytest manages cleanup)."""
    return tmp_path


@pytest.fixture
def experiment_logger():
    """Get the experiment logger for the current session."""
    return _plugin.logger if _plugin else None


@pytest.fixture
def setup_test_context(test_dir):
    """Factory fixture to set up test context with skills and CLAUDE.md.

    Uses shell scripts for file operations.
    """
    def _setup(skills: dict = None, claude_md: str = None, environment_dir: Path = None):
        # Write CLAUDE.md using shell
        if claude_md:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(claude_md)
                temp_file = f.name
            try:
                run_shell("setup.sh", "write-claude-md", str(test_dir), temp_file)
            finally:
                os.unlink(temp_file)

        # Write each skill using shell
        if skills:
            for skill_name, skill_config in skills.items():
                if skill_config:
                    # Support both formats:
                    # 1. List of sections: {"skill-name": [section1, section2]}
                    # 2. Dict with sections and scripts: {"sections": [...], "scripts_dir": Path}
                    if isinstance(skill_config, dict):
                        sections = skill_config.get("sections", [])
                        scripts_dir = skill_config.get("scripts_dir")
                    else:
                        sections = skill_config
                        scripts_dir = None

                    if sections:
                        content = "\n\n".join(s for s in sections if s and s.strip())
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                            f.write(content)
                            temp_file = f.name
                        try:
                            args = ["write-skill", str(test_dir), skill_name, temp_file]
                            if scripts_dir:
                                args.append(str(scripts_dir))
                            run_shell("setup.sh", *args)
                        finally:
                            os.unlink(temp_file)

        # Copy environment files using shell
        if environment_dir and environment_dir.exists():
            run_shell("setup.sh", "copy-env", str(test_dir), str(environment_dir))

        return test_dir
    return _setup


@pytest.fixture
def run_claude(test_dir, experiment_logger, request):
    """Factory fixture to run Claude in Docker and capture artifacts.

    This fixture automatically:
    - Runs Claude with the given prompt
    - Saves raw output to the experiment logs
    - Returns the result for further processing
    """
    def _run(prompt: str, timeout: int = 600, model: str = None):
        result = run_claude_in_docker(test_dir, prompt, timeout=timeout, model=model)

        # Save raw output if we have a logger
        if experiment_logger and hasattr(request, 'node'):
            treatment_name = _get_treatment_name(request.node)
            rep = _plugin.get_rep_number(treatment_name) if _plugin else 1
            save_raw(
                experiment_logger.base_dir,
                treatment_name,
                rep,
                result.stdout,
                result.stderr,
            )

        return result

    return _run


@pytest.fixture
def run_python_file(test_dir):
    """Factory fixture to run Python files in Docker."""
    def _run(filename: str, timeout: int = 300):
        return run_python_in_docker(test_dir, filename, timeout=timeout)
    return _run


@pytest.fixture
def record_result(test_dir, experiment_logger, request):
    """Factory fixture to record validation results and save artifacts.

    Usage:
        result = run_claude(prompt)
        events = extract_events(parse_output(result.stdout))
        passed, failed = treatment.validate(events, test_dir, {})
        record_result(events, passed, failed, run_id="abc123")
    """
    def _record(
        events: Dict[str, Any],
        passed: List[str],
        failed: List[str],
        run_id: str = "",
    ):
        if not experiment_logger:
            return

        treatment_name = _get_treatment_name(request.node)
        # Use existing rep number (already incremented by run_claude)
        rep = _plugin.run_counter.get(treatment_name, 1) if _plugin else 1

        base_dir = experiment_logger.base_dir

        # Save events
        save_events(base_dir, treatment_name, rep, events)

        # Save artifacts (files Claude generated)
        _save_artifacts(base_dir, treatment_name, rep, test_dir)

        # Save report
        report = {
            "name": treatment_name,
            "rep": rep,
            "passed": len(failed) == 0,
            "run_id": run_id,
            "checks_passed": passed,
            "checks_failed": failed,
            "events_summary": {
                "duration_seconds": events.get("duration_seconds"),
                "num_turns": events.get("num_turns"),
                "tool_calls": len(events.get("tool_calls", [])),
                "files_created": events.get("files_created", []),
                "skills_invoked": events.get("skills_invoked", []),
            },
            "timestamp": datetime.now().isoformat(),
        }
        save_report(base_dir, treatment_name, rep, report)

        # Add to logger
        experiment_logger.add_result(
            treatment_name,
            TreatmentResult(
                name=treatment_name,
                passed=len(failed) == 0,
                checks_passed=passed,
                checks_failed=failed,
                events_summary={
                    "num_turns": events.get("num_turns"),
                    "duration_seconds": events.get("duration_seconds"),
                    "tool_calls": len(events.get("tool_calls", [])),
                },
                run_id=run_id,
            )
        )

    return _record


# =============================================================================
# HELPERS
# =============================================================================

def _get_treatment_name(node) -> str:
    """Extract treatment name from pytest node."""
    # test_treatment[TREATMENT_NAME] -> TREATMENT_NAME
    nodeid = node.nodeid
    if "[" in nodeid:
        return nodeid.split("[")[1].rstrip("]")
    return nodeid.split("::")[-1]


def _save_artifacts(base_dir: Path, treatment_name: str, rep: int, test_dir: Path):
    """Save Claude's generated files as artifacts."""
    artifacts_dir = base_dir / "artifacts" / f"{treatment_name.lower()}_rep{rep}"
    claude_dir = artifacts_dir / "claude"
    execution_dir = artifacts_dir / "execution"
    claude_dir.mkdir(parents=True, exist_ok=True)
    execution_dir.mkdir(parents=True, exist_ok=True)

    # Files to exclude (environment files)
    env_files = {"sql_agent.py", "chinook.db", "requirements.txt", "Dockerfile"}

    # Copy files Claude generated
    for f in test_dir.iterdir():
        if f.is_file() and f.name not in env_files and not f.name.startswith("."):
            try:
                shutil.copy(f, claude_dir / f.name)
            except Exception:
                pass

    # Run Python files and save execution output
    py_files = [f for f in test_dir.glob("*.py") if f.name not in env_files]
    for py_file in py_files:
        try:
            success, output = run_python_in_docker(test_dir, py_file.name, timeout=300)
            status = "success" if success else "error"
            output_file = execution_dir / f"{py_file.stem}_{status}.txt"
            output_file.write_text(strip_ansi(output))
        except Exception as e:
            error_file = execution_dir / f"{py_file.stem}_error.txt"
            error_file.write_text(str(e))
