"""Test runner for Claude Code CLI (parallel execution)."""

import os
import subprocess
import hashlib
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Pool
from typing import Dict, Any, List, Callable
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from .logging import (
    parse_output, extract_events, strip_ansi,
    save_events, save_raw, save_report,
)
from .setup import (
    check_docker_available,
    setup_test_environment, cleanup_test_environment, setup_test_context,
    write_skill, get_noise_skill_content,
)


# =============================================================================
# DOCKER
# =============================================================================

DOCKER_IMAGE_PREFIX = "skillbench"


def build_docker_image(test_dir: Path, force: bool = False, verbose: bool = False) -> str | None:
    """Build Docker image from Dockerfile in test directory."""
    dockerfile = test_dir / "Dockerfile"
    if not dockerfile.exists():
        return None

    dockerfile_hash = hashlib.md5(dockerfile.read_bytes()).hexdigest()[:8]
    image_name = f"{DOCKER_IMAGE_PREFIX}:{dockerfile_hash}"

    if not force:
        result = subprocess.run(
            ["docker", "images", "-q", image_name],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            return image_name

    if verbose:
        result = subprocess.run(
            ["docker", "build", "-t", image_name, "-f", str(dockerfile), str(test_dir)],
            timeout=300
        )
    else:
        result = subprocess.run(
            ["docker", "build", "-t", image_name, "-f", str(dockerfile), str(test_dir)],
            capture_output=True, text=True, timeout=300
        )

    if result.returncode == 0:
        return image_name
    return None


def run_in_docker(
    image_name: str,
    test_dir: Path,
    command: List[str],
    timeout: int = 120,
    env_vars: Dict[str, str] = None,
) -> subprocess.CompletedProcess:
    """Run a command inside a Docker container."""
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{test_dir}:/workspace",
        "-w", "/workspace",
    ]

    env_vars = env_vars or {}
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_TRACING", "LANGSMITH_ENDPOINT", "TAVILY_API_KEY"]:
        if key in os.environ:
            env_vars[key] = os.environ[key]

    for key, value in env_vars.items():
        docker_cmd.extend(["-e", f"{key}={value}"])

    docker_cmd.append(image_name)
    docker_cmd.extend(command)

    return subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)


def run_python_in_docker(test_dir: Path, script_name: str, timeout: int = 120) -> tuple[bool, str]:
    """Run a Python script in Docker container. Returns (success, output)."""
    if not check_docker_available():
        return False, "Docker not available"

    image_name = build_docker_image(test_dir)
    if not image_name:
        return False, "No Dockerfile or build failed"

    try:
        result = run_in_docker(image_name, test_dir, ["python", script_name], timeout=timeout)
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout}s)"
    except Exception as e:
        return False, str(e)


def run_claude_in_docker(
    test_dir: Path,
    prompt: str,
    timeout: int = 300,
    model: str = None,
) -> subprocess.CompletedProcess:
    """Run Claude Code CLI inside Docker container for security."""
    if not check_docker_available():
        raise RuntimeError("Docker not available")

    image_name = build_docker_image(test_dir, verbose=False)
    if not image_name:
        raise RuntimeError("Failed to build Docker image")

    claude_cmd = [
        "claude", "-p", prompt,
        "--dangerously-skip-permissions",
        "--output-format", "stream-json",
        "--verbose",
    ]
    if model:
        claude_cmd.extend(["--model", model])

    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{test_dir}:/workspace",
        "-w", "/workspace",
    ]

    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_TRACING", "LANGSMITH_ENDPOINT", "TAVILY_API_KEY"]:
        if key in os.environ:
            docker_cmd.extend(["-e", f"{key}={os.environ[key]}"])

    docker_cmd.append(image_name)
    docker_cmd.extend(claude_cmd)

    return subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)


# =============================================================================
# TEST RESULT
# =============================================================================

@dataclass
class TestResult:
    name: str
    passed: bool
    checks_passed: List[str]
    checks_failed: List[str]
    events: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict for multiprocessing."""
        return {
            "name": self.name,
            "passed": self.passed,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "events": self.events,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TestResult":
        """Reconstruct from dict."""
        return cls(**d)


# =============================================================================
# WORK ITEM
# =============================================================================

@dataclass
class WorkItem:
    """A single unit of work for parallel execution."""
    treatment_name: str
    rep: int
    base_dir: str  # String for pickling
    prompt: str
    skills: Dict[str, Any]
    claude_md: str
    noise_tasks: List[str]
    environment_dir: str  # String for pickling
    timeout: int = 600
    model: str = None
    files_to_run: List[str] = None  # Files to run for validation (None = all .py files)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dict for multiprocessing."""
        return {
            "treatment_name": self.treatment_name,
            "rep": self.rep,
            "base_dir": self.base_dir,
            "prompt": self.prompt,
            "skills": self.skills,
            "claude_md": self.claude_md,
            "noise_tasks": self.noise_tasks,
            "environment_dir": self.environment_dir,
            "timeout": self.timeout,
            "model": self.model,
            "files_to_run": self.files_to_run,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WorkItem":
        """Reconstruct from dict."""
        return cls(**d)

    @property
    def file_prefix(self) -> str:
        """File naming prefix: treatment_rep_date."""
        date = datetime.now().strftime("%Y%m%d")
        return f"{self.treatment_name.lower()}_rep{self.rep}_{date}"


# =============================================================================
# PARALLEL EXECUTION
# =============================================================================

def run_single(args: tuple) -> Dict[str, Any]:
    """Run a single treatment/rep in a worker process.

    Args:
        args: Tuple of (WorkItem dict, validator_func)

    Returns:
        Dict with treatment_name, rep, and serialized result
    """
    work_dict, validate_func = args
    work = WorkItem.from_dict(work_dict)
    base_dir = Path(work.base_dir)
    environment_dir = Path(work.environment_dir) if work.environment_dir else None

    prefix = work.file_prefix
    print(f"[{prefix}] Starting...", flush=True)

    # Setup test directory
    test_dir = setup_test_environment()
    setup_test_context(
        test_dir,
        skills=work.skills,
        claude_md=work.claude_md,
        environment_dir=environment_dir,
    )

    # Add noise skills if any
    for noise_skill in work.noise_tasks:
        content = get_noise_skill_content(noise_skill)
        if content:
            write_skill(test_dir, noise_skill, content)

    print(f"[{prefix}] Running Claude in Docker...", flush=True)
    start_time = datetime.now()

    try:
        result = run_claude_in_docker(
            test_dir, work.prompt,
            timeout=work.timeout,
            model=work.model
        )
        duration = (datetime.now() - start_time).total_seconds()
        print(f"[{prefix}] Claude completed in {duration:.1f}s", flush=True)

        # Save raw output
        save_raw(base_dir, work.treatment_name, work.rep, result.stdout, result.stderr)

        # Parse events
        events = extract_events(parse_output(result.stdout))
        print(f"[{prefix}] Extracted {len(events.get('tool_calls', []))} tool calls", flush=True)

    except subprocess.TimeoutExpired as e:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"[{prefix}] TIMEOUT after {duration:.1f}s", flush=True)

        # Capture partial output from timeout exception (may be bytes or str)
        partial_stdout = e.stdout or ""
        partial_stderr = e.stderr or ""

        # Convert bytes to str if needed
        if isinstance(partial_stdout, bytes):
            partial_stdout = partial_stdout.decode('utf-8', errors='replace')
        if isinstance(partial_stderr, bytes):
            partial_stderr = partial_stderr.decode('utf-8', errors='replace')

        if partial_stdout or partial_stderr:
            print(f"[{prefix}] Captured {len(partial_stdout)} chars of partial output", flush=True)
            save_raw(base_dir, work.treatment_name, work.rep, partial_stdout, partial_stderr)

            # Try to parse partial events
            events = extract_events(parse_output(partial_stdout))
            save_events(base_dir, work.treatment_name, work.rep, events)
            print(f"[{prefix}] Saved {len(events.get('tool_calls', []))} tool calls from partial output", flush=True)
        else:
            events = {}
            print(f"[{prefix}] No partial output captured", flush=True)

        cleanup_test_environment(test_dir)
        return {
            "treatment_name": work.treatment_name,
            "rep": work.rep,
            "result": TestResult(
                name=work.treatment_name,
                passed=False,
                checks_passed=[],
                checks_failed=[f"Timeout after {duration:.1f}s"],
                events=events,
            ).to_dict()
        }
    except Exception as e:
        print(f"[{prefix}] ERROR: {e}", flush=True)
        cleanup_test_environment(test_dir)
        return {
            "treatment_name": work.treatment_name,
            "rep": work.rep,
            "result": TestResult(
                name=work.treatment_name,
                passed=False,
                checks_passed=[],
                checks_failed=[str(e)],
                events={},
            ).to_dict()
        }

    # Save events
    save_events(base_dir, work.treatment_name, work.rep, events)

    # Setup output directories
    code_dir = base_dir / "code" / f"{work.treatment_name.lower()}_rep{work.rep}"
    code_dir.mkdir(parents=True, exist_ok=True)
    docker_dir = base_dir / "docker" / f"{work.treatment_name.lower()}_rep{work.rep}"
    docker_dir.mkdir(parents=True, exist_ok=True)

    # Run Python files ONCE and capture outputs (reused for validation and logging)
    # Use files_to_run if specified, otherwise run all .py files
    if work.files_to_run:
        py_files = [test_dir / f for f in work.files_to_run if (test_dir / f).exists()]
        print(f"[{prefix}] Running {len(py_files)} specified files: {work.files_to_run}", flush=True)
    else:
        py_files = list(test_dir.glob("*.py"))
        print(f"[{prefix}] Running all {len(py_files)} Python files", flush=True)

    outputs = {}  # {filename: (success, output, duration_seconds)}
    for py_file in py_files:
        # Copy code file to logs
        (code_dir / py_file.name).write_text(py_file.read_text())

        # Run and capture output with timing
        print(f"[{prefix}] Running {py_file.name} in Docker...", flush=True)
        run_start = datetime.now()
        try:
            success, output = run_python_in_docker(test_dir, py_file.name, timeout=180)
            duration = (datetime.now() - run_start).total_seconds()
            outputs[py_file.name] = (success, output, duration)

            status = "success" if success else "error"
            print(f"[{prefix}] {py_file.name}: {status} in {duration:.1f}s ({len(output)} chars)", flush=True)

            # Save docker output to logs
            output_file = docker_dir / f"{py_file.stem}_{status}.txt"
            output_file.write_text(strip_ansi(output))
        except Exception as e:
            duration = (datetime.now() - run_start).total_seconds()
            outputs[py_file.name] = (False, str(e), duration)
            print(f"[{prefix}] {py_file.name}: error in {duration:.1f}s - {e}", flush=True)

            error_file = docker_dir / f"{py_file.stem}_error.txt"
            error_file.write_text(str(e))

    # Run validation with pre-captured outputs (no re-running)
    print(f"[{prefix}] Running validation...", flush=True)
    passed, failed = validate_func(events, test_dir, work.treatment_name, outputs)
    ok = len(failed) == 0

    status = "PASS" if ok else "FAIL"
    print(f"[{prefix}] Result: {status} ({len(passed)} passed, {len(failed)} failed)", flush=True)

    # Save report
    report = {
        "name": work.treatment_name,
        "rep": work.rep,
        "passed": ok,
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
    save_report(base_dir, work.treatment_name, work.rep, report)

    # Cleanup
    cleanup_test_environment(test_dir)

    return {
        "treatment_name": work.treatment_name,
        "rep": work.rep,
        "result": TestResult(
            name=work.treatment_name,
            passed=ok,
            checks_passed=passed,
            checks_failed=failed,
            events=events,
        ).to_dict()
    }


def run_parallel(
    work_items: List[WorkItem],
    validate_func: Callable[[Dict, Path, str], tuple[List[str], List[str]]],
    max_workers: int = 3,
) -> Dict[str, List[TestResult]]:
    """Run treatments in parallel using multiprocessing.

    Args:
        work_items: List of WorkItem objects
        validate_func: Validation function (must be picklable)
        max_workers: Max parallel workers (default 3 to avoid API rate limits)

    Returns:
        Dict mapping treatment names to lists of TestResult
    """
    work_args = [(w.to_dict(), validate_func) for w in work_items]

    print(f"\nRunning {len(work_items)} tasks with {max_workers} parallel workers...\n")

    with Pool(max_workers) as pool:
        raw_results = pool.map(run_single, work_args)

    # Aggregate results
    results: Dict[str, List[TestResult]] = {}
    for raw in raw_results:
        treatment_name = raw["treatment_name"]
        result = TestResult.from_dict(raw["result"])

        if treatment_name not in results:
            results[treatment_name] = []
        results[treatment_name].append(result)

    return results


def create_work_items(
    treatments: Dict[str, Any],
    treatment_names: List[str],
    base_dir: Path,
    build_prompt_func: Callable,
    environment_dir: Path,
    repeat: int = 1,
    timeout: int = 600,
    model: str = None,
) -> List[WorkItem]:
    """Create WorkItem objects for all treatments and repetitions.

    Args:
        treatments: Dict mapping treatment names to Treatment objects
        treatment_names: List of treatment names to run
        base_dir: Experiment base directory for logging
        build_prompt_func: Function(treatment, name) -> prompt string
        environment_dir: Path to environment files
        repeat: Number of repetitions per treatment
        timeout: Timeout per run in seconds
        model: Optional model override

    Returns:
        List of WorkItem objects
    """
    items = []

    for treatment_name in treatment_names:
        treatment = treatments[treatment_name]
        prompt = build_prompt_func(treatment, treatment_name)

        # Get files to run from treatment (if method exists)
        files_to_run = None
        if hasattr(treatment, 'get_files_to_run'):
            files_to_run = treatment.get_files_to_run() or None

        for rep in range(1, repeat + 1):
            items.append(WorkItem(
                treatment_name=treatment_name,
                rep=rep,
                base_dir=str(base_dir),
                prompt=prompt,
                skills=treatment.skills or {},
                claude_md=treatment.claude_md or "",
                noise_tasks=treatment.noise_tasks or [],
                environment_dir=str(environment_dir),
                timeout=timeout,
                model=model,
                files_to_run=files_to_run,
            ))

    return items
