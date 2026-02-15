"""Shared pytest fixtures and experiment logging plugin.

Generates rich experiment logs in logs/experiments/ including:
- summary.md: Full markdown report with tables and details
- events/: Parsed events from each test run
- raw/: Raw Claude CLI output
- reports/: Per-run validation reports
- artifacts/: Files Claude generated and their execution output
- metadata.json: Experiment metadata

Supports pytest-xdist parallel execution via worker coordination.
"""

import fcntl
import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from dotenv import load_dotenv

from scaffold import run_claude_in_docker, run_python_in_docker, run_shell
from scaffold.python import (
    ExperimentLogger,
    TreatmentResult,
    save_events,
    save_raw,
    save_report,
    strip_ansi,
)

PROJECT_ROOT = Path(__file__).parent.parent

# Shared file for xdist worker coordination
XDIST_EXPERIMENT_FILE = PROJECT_ROOT / ".pytest_experiment_id"
DOCKER_BUILD_LOCK = PROJECT_ROOT / ".pytest_docker_build.lock"


# =============================================================================
# EXPERIMENT LOGGING PLUGIN
# =============================================================================


def _get_experiment_name(session) -> str:
    """Determine experiment name from test path."""
    items = getattr(session, "items", None)
    first_path = str(items[0].fspath) if items else ""

    if "bench_lc_basic" in first_path:
        if "guidance" in first_path:
            return "lc_guide"
        elif "claudemd" in first_path:
            return "lc_claude"
        elif "noise" in first_path:
            return "lc_noise"
        return "lc_basic"
    elif "bench_ls_multiskill" in first_path:
        if "basic" in first_path:
            return "ls_basic"
        elif "advanced" in first_path:
            return "ls_adv"
        return "ls_multi"
    elif "example" in first_path:
        return "example"
    return "experiment"


def _get_or_create_experiment_id(name: str, use_coordination: bool) -> str:
    """Get shared experiment ID or create new one.

    Uses file locking to coordinate between xdist workers and master.
    """
    if not use_coordination:
        # Not using xdist, create fresh experiment
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{timestamp}"

    # Using xdist - coordinate via shared file
    lock_file = XDIST_EXPERIMENT_FILE.with_suffix(".lock")

    with open(lock_file, "w") as lf:
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        try:
            if XDIST_EXPERIMENT_FILE.exists():
                # Another worker already created experiment
                data = json.loads(XDIST_EXPERIMENT_FILE.read_text())
                return data["experiment_id"]
            else:
                # First worker - create experiment
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                experiment_id = f"{name}_{timestamp}"
                XDIST_EXPERIMENT_FILE.write_text(
                    json.dumps(
                        {
                            "experiment_id": experiment_id,
                            "created_at": datetime.now().isoformat(),
                        }
                    )
                )
                return experiment_id
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)


def _cleanup_experiment_coordination():
    """Remove coordination files after experiment."""
    for f in [XDIST_EXPERIMENT_FILE, XDIST_EXPERIMENT_FILE.with_suffix(".lock")]:
        try:
            f.unlink(missing_ok=True)
        except Exception:
            pass


class ExperimentPlugin:
    """Pytest plugin that generates rich experiment logs in logs/experiments/.

    Supports pytest-xdist parallel execution by coordinating workers via
    a shared file to ensure all workers log to the same experiment folder.
    """

    def __init__(self, config):
        self.config = config
        self.logger: ExperimentLogger | None = None
        self.start_time = None
        self.run_counter: dict[str, int] = {}  # treatment_name -> repetition count
        self.is_xdist_worker = hasattr(config, "workerinput")
        self.is_xdist_master = (
            hasattr(config, "workerinput") is False
            and (getattr(config.option, "numprocesses", None) or 0) > 0
        )
        self.worker_id = (
            config.workerinput.get("workerid", "master") if self.is_xdist_worker else "master"
        )

    def pytest_sessionstart(self, session):
        """Create or join experiment logger at session start."""
        name = _get_experiment_name(session)

        # Get or create shared experiment ID (master also participates when xdist is active)
        use_coordination = self.is_xdist_worker or self.is_xdist_master
        experiment_id = _get_or_create_experiment_id(name, use_coordination)

        # Join existing experiment (workers) or create new (master/single)
        self.logger = ExperimentLogger(experiment_name=name, experiment_id=experiment_id)
        self.start_time = time.time()

        print(f"\n{'=' * 60}")
        print(f"EXPERIMENT: {self.logger.experiment_id}")
        print(f"Logging to: {self.logger.base_dir}")
        print(f"{'=' * 60}\n")

    def get_rep_number(self, treatment_name: str) -> int:
        """Get the next repetition number for a treatment."""
        if treatment_name not in self.run_counter:
            self.run_counter[treatment_name] = 0
        self.run_counter[treatment_name] += 1
        return self.run_counter[treatment_name]

    def pytest_sessionfinish(self, session, exitstatus):
        """Generate and save summary at session end.

        With xdist, only the master process generates the final summary
        after all workers complete.
        """
        if not self.logger:
            return

        # Workers: just ensure their results are saved (already done via record_result)
        # Master/single: generate summary from all saved reports
        if self.is_xdist_worker:
            # Worker done - results already saved to files
            return

        # Master or single process - wait briefly for workers to finish writing
        if self.is_xdist_master:
            time.sleep(1)  # Brief wait for file system sync

        # Reload results from report files (aggregates all workers)
        self._reload_results_from_reports()

        if self.logger.results:
            self.logger.finalize()
            self._print_summary()

        # Cleanup coordination files
        _cleanup_experiment_coordination()

    def _reload_results_from_reports(self):
        """Reload results from saved report files (aggregates all workers)."""
        reports_dir = self.logger.reports_dir
        if not reports_dir.exists():
            return

        for report_file in sorted(reports_dir.glob("*.json")):
            try:
                report = json.loads(report_file.read_text())
                treatment_name = report.get("name", "unknown")
                result = TreatmentResult(
                    name=treatment_name,
                    passed=report.get("passed", False),
                    checks_passed=report.get("checks_passed", []),
                    checks_failed=report.get("checks_failed", []),
                    events_summary=report.get("events_summary", {}),
                    run_id=report.get("run_id", ""),
                )
                if treatment_name not in self.logger.results:
                    self.logger.results[treatment_name] = []
                self.logger.results[treatment_name].append(result)
            except Exception:
                pass

    def _print_summary(self):
        """Print summary to console."""
        print(f"\n{'=' * 80}")
        print("  RESULTS")
        print(f"{'=' * 80}\n")

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
        total_passed = sum(
            sum(len(r.checks_passed) for r in runs) for runs in self.logger.results.values()
        )
        total_checks = sum(
            sum(len(r.checks_passed) + len(r.checks_failed) for r in runs)
            for runs in self.logger.results.values()
        )
        if total_checks:
            print(
                f"Total: {total_passed}/{total_checks} checks passed ({total_passed / total_checks * 100:.1f}%)"
            )
        print(f"{'=' * 80}")


# Global plugin instance (set during pytest_configure)
_plugin: ExperimentPlugin | None = None


def pytest_configure(config):
    """Register experiment plugin."""
    global _plugin
    _plugin = ExperimentPlugin(config)
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


def _build_docker_image_with_lock(environment_dir: Path) -> str | None:
    """Build Docker image with file locking to prevent race conditions.

    Uses file locking to ensure only one process builds the image at a time.
    Other processes wait for the build to complete, then use the cached image.
    """
    if not environment_dir or not (environment_dir / "Dockerfile").exists():
        return None

    # Create lock file
    lock_file = DOCKER_BUILD_LOCK

    with open(lock_file, "w") as lf:
        # Acquire exclusive lock (blocks until available)
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        try:
            # Build image (will use cache if already built by another process)
            result = run_shell("docker.sh", "build", str(environment_dir), timeout=300, check=False)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)


@pytest.fixture(scope="session", autouse=True)
def prebuild_docker_image(request):
    """Pre-build Docker image once per session to avoid race conditions.

    This fixture uses file locking to ensure only one worker builds the image.
    Other workers wait for the build to complete.

    Tests should depend on this fixture via environment_dir fixture.
    """
    # Find environment_dir from test module if available
    # This is a session fixture, so we build for common environments
    for marker in ["bench_lc_basic", "bench_ls_multiskill"]:
        env_dir = PROJECT_ROOT / "tests" / marker / "environment"
        if env_dir.exists():
            image = _build_docker_image_with_lock(env_dir)
            if image:
                print(f"\nPre-built Docker image: {image}")

    yield

    # Cleanup lock file at session end (only if we're the last one)
    try:
        DOCKER_BUILD_LOCK.unlink(missing_ok=True)
    except Exception:
        pass


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
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
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
                        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
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
        if experiment_logger and hasattr(request, "node"):
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
        events: dict[str, Any],
        passed: list[str],
        failed: list[str],
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
            ),
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
