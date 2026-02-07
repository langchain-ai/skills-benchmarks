"""Test runner for Claude Code CLI.

Executes tests through a 4-phase pipeline:
1. SETUP: Create isolated test environment with skills
2. EXECUTION: Run Claude in Docker
3. GROUND TRUTH: Run generated files to capture outputs
4. VALIDATION: Check outputs against validators

Supports parallel execution across treatments.
"""

import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from multiprocessing import Pool
from typing import Dict, Any, List, Callable
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from .logging import parse_output, extract_events, strip_ansi, save_events, save_raw, save_report
from .setup import setup_test_environment, cleanup_test_environment, setup_test_context, write_skill, get_noise_skill_content
from .utils import run_python_in_docker, run_claude_in_docker


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TestResult:
    """Result of a single test run."""
    name: str
    passed: bool
    checks_passed: List[str]
    checks_failed: List[str]
    events: Dict[str, Any]
    run_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in ['name', 'passed', 'checks_passed', 'checks_failed', 'events', 'run_id']}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TestResult":
        return cls(**d)


@dataclass
class WorkItem:
    """Configuration for a single test run."""
    treatment_name: str
    rep: int
    base_dir: str  # String for pickling
    prompt: str
    skills: Dict[str, Any] = field(default_factory=dict)
    claude_md: str = ""
    noise_tasks: List[str] = field(default_factory=list)
    environment_dir: str = ""
    timeout: int = 600
    model: str = None
    files_to_run: List[str] = None  # Specific files to run, or None for all .py
    run_id: str = ""  # Unique ID for this run (used for dataset naming)

    @property
    def prefix(self) -> str:
        return f"{self.treatment_name.lower()}_rep{self.rep}_{datetime.now().strftime('%Y%m%d')}"

    def to_dict(self) -> Dict[str, Any]:
        return {f: getattr(self, f) for f in [
            'treatment_name', 'rep', 'base_dir', 'prompt', 'skills', 'claude_md',
            'noise_tasks', 'environment_dir', 'timeout', 'model', 'files_to_run', 'run_id',
        ]}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WorkItem":
        return cls(**d)


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_single(args: tuple) -> Dict[str, Any]:
    """Run a single test through the 4-phase pipeline.

    Args:
        args: (WorkItem dict, validate_func)
              validate_func signature: (events, test_dir, treatment_name, outputs) -> (passed, failed)

    Returns:
        {treatment_name, rep, result: TestResult dict}
    """
    work_dict, validate_func = args
    work = WorkItem.from_dict(work_dict)
    base_dir = Path(work.base_dir)
    prefix = work.prefix

    print(f"[{prefix}] Starting...", flush=True)

    # -------------------------------------------------------------------------
    # PHASE 1: SETUP - Create isolated test environment
    # -------------------------------------------------------------------------
    test_dir = setup_test_environment()
    environment_dir = Path(work.environment_dir) if work.environment_dir else None

    setup_test_context(
        test_dir,
        skills=work.skills,
        claude_md=work.claude_md,
        environment_dir=environment_dir,
    )

    for noise_skill in work.noise_tasks:
        content = get_noise_skill_content(noise_skill)
        if content:
            write_skill(test_dir, noise_skill, content)

    # -------------------------------------------------------------------------
    # PHASE 2: EXECUTION - Run Claude in Docker
    # -------------------------------------------------------------------------
    print(f"[{prefix}] Running Claude...", flush=True)
    start = datetime.now()

    try:
        result = run_claude_in_docker(test_dir, work.prompt, timeout=work.timeout, model=work.model)
        duration = (datetime.now() - start).total_seconds()
        print(f"[{prefix}] Claude completed in {duration:.1f}s", flush=True)

        save_raw(base_dir, work.treatment_name, work.rep, result.stdout, result.stderr)
        events = extract_events(parse_output(result.stdout))
        print(f"[{prefix}] Extracted {len(events.get('tool_calls', []))} tool calls", flush=True)

    except subprocess.TimeoutExpired as e:
        print(f"[{prefix}] TIMEOUT after {work.timeout}s", flush=True)
        # Try to capture partial output
        stdout = (e.stdout or b"").decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = (e.stderr or b"").decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else (e.stderr or "")
        if stdout or stderr:
            save_raw(base_dir, work.treatment_name, work.rep, stdout, stderr)
            events = extract_events(parse_output(stdout))
            save_events(base_dir, work.treatment_name, work.rep, events)
        cleanup_test_environment(test_dir)
        return _result(work, False, [], [f"Timeout after {work.timeout}s"], events if 'events' in dir() else {})

    except Exception as e:
        print(f"[{prefix}] ERROR: {e}", flush=True)
        cleanup_test_environment(test_dir)
        return _result(work, False, [], [str(e)], {})

    save_events(base_dir, work.treatment_name, work.rep, events)

    # -------------------------------------------------------------------------
    # PHASE 3: GROUND TRUTH - Run generated files AND generate expected outputs
    # -------------------------------------------------------------------------
    outputs = _run_generated_files(work, test_dir, base_dir, prefix)

    # Copy shared ground truth (generated once at experiment start in base_dir/ground_truth/)
    shared_gt_dir = base_dir / "ground_truth"
    if shared_gt_dir.exists():
        print(f"[{prefix}] Copying shared ground truth...", flush=True)
        expected_dir = base_dir / "artifacts" / f"{work.treatment_name.lower()}_rep{work.rep}" / "expected"
        expected_dir.mkdir(parents=True, exist_ok=True)

        for gt_file in ["expected_traces.json", "expected_dataset.json", "evaluator_test_cases.json"]:
            src = shared_gt_dir / gt_file
            if src.exists():
                # Copy to expected dir AND test_dir (for validator access)
                (expected_dir / gt_file).write_text(src.read_text())
                (test_dir / gt_file).write_text(src.read_text())
        print(f"[{prefix}] Ground truth copied", flush=True)

    # -------------------------------------------------------------------------
    # PHASE 4: VALIDATION - Check outputs against validators
    # -------------------------------------------------------------------------
    # Add run_id to outputs so validators can find the correct uploaded dataset
    outputs["_run_id"] = work.run_id
    print(f"[{prefix}] Validating...", flush=True)
    passed, failed = validate_func(events, test_dir, work.treatment_name, outputs)
    ok = len(failed) == 0

    print(f"[{prefix}] {'PASS' if ok else 'FAIL'} ({len(passed)} passed, {len(failed)} failed)", flush=True)

    # Save report
    save_report(base_dir, work.treatment_name, work.rep, {
        "name": work.treatment_name, "rep": work.rep, "passed": ok,
        "run_id": work.run_id,  # For finding LangSmith assets (test-{run_id})
        "checks_passed": passed, "checks_failed": failed,
        "events_summary": {
            "duration_seconds": events.get("duration_seconds"),
            "num_turns": events.get("num_turns"),
            "tool_calls": len(events.get("tool_calls", [])),
            "files_created": events.get("files_created", []),
            "skills_invoked": events.get("skills_invoked", []),
        },
        "timestamp": datetime.now().isoformat(),
    })

    cleanup_test_environment(test_dir)
    return _result(work, ok, passed, failed, events)


def _run_generated_files(work: WorkItem, test_dir: Path, base_dir: Path, prefix: str) -> Dict[str, tuple]:
    """Run Python files Claude created and capture outputs.

    Returns: {filename: (success, output, duration_seconds)}
    """
    run_dir = base_dir / "artifacts" / f"{work.treatment_name.lower()}_rep{work.rep}"
    claude_dir = run_dir / "claude"
    execution_dir = run_dir / "execution"
    claude_dir.mkdir(parents=True, exist_ok=True)
    execution_dir.mkdir(parents=True, exist_ok=True)

    # Save ALL files Claude generated (exclude environment files and .claude/)
    env_files = {"sql_agent.py", "chinook.db", "requirements.txt", "Dockerfile"}
    for f in test_dir.iterdir():
        if f.is_file() and f.name not in env_files and not f.name.startswith("."):
            (claude_dir / f.name).write_text(f.read_text())

    # Determine files to run
    if work.files_to_run:
        py_files = [test_dir / f for f in work.files_to_run if (test_dir / f).exists()]
    else:
        py_files = [f for f in test_dir.glob("*.py") if f.name not in env_files]

    outputs = {}
    for py_file in py_files:
        start = datetime.now()
        try:
            success, output = run_python_in_docker(test_dir, py_file.name, timeout=300)
            dur = (datetime.now() - start).total_seconds()
            outputs[py_file.name] = (success, output, dur)
            status = "success" if success else "error"
            print(f"[{prefix}] {py_file.name}: {status} ({dur:.1f}s)", flush=True)
            (execution_dir / f"{py_file.stem}_{status}.txt").write_text(strip_ansi(output))
        except Exception as e:
            dur = (datetime.now() - start).total_seconds()
            outputs[py_file.name] = (False, str(e), dur)
            print(f"[{prefix}] {py_file.name}: error ({dur:.1f}s)", flush=True)
            (execution_dir / f"{py_file.stem}_error.txt").write_text(str(e))

    return outputs


def _result(work: WorkItem, ok: bool, passed: List[str], failed: List[str], events: Dict) -> Dict:
    """Create result dict for multiprocessing return."""
    return {
        "treatment_name": work.treatment_name,
        "rep": work.rep,
        "result": TestResult(work.treatment_name, ok, passed, failed, events, work.run_id).to_dict()
    }


# =============================================================================
# PARALLEL EXECUTION
# =============================================================================

def run_parallel(
    work_items: List[WorkItem],
    validate_func: Callable,
    max_workers: int = 3,
) -> Dict[str, List[TestResult]]:
    """Run treatments in parallel.

    Args:
        work_items: List of WorkItem configurations
        validate_func: (events, test_dir, treatment_name, outputs) -> (passed, failed)
        max_workers: Max parallel workers (default 3 to avoid API rate limits)

    Returns:
        {treatment_name: [TestResult, ...]}
    """
    print(f"\nRunning {len(work_items)} tasks with {max_workers} workers...\n")

    with Pool(max_workers) as pool:
        raw_results = pool.map(run_single, [(w.to_dict(), validate_func) for w in work_items])

    results: Dict[str, List[TestResult]] = {}
    for raw in raw_results:
        name = raw["treatment_name"]
        if name not in results:
            results[name] = []
        results[name].append(TestResult.from_dict(raw["result"]))
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
    """Create WorkItem for each treatment x repetition.

    Args:
        build_prompt_func: (treatment, name, rep, run_id) -> prompt string

    Note: Ground truth should be pre-generated to base_dir/ground_truth/ before running.
          The runner will automatically copy it to each treatment's expected/ directory.
    """
    import uuid
    items = []
    for name in treatment_names:
        treatment = treatments[name]
        files_to_run = treatment.get_files_to_run() if hasattr(treatment, 'get_files_to_run') else None

        for rep in range(1, repeat + 1):
            # Generate unique run_id for dataset naming and validator matching
            run_id = uuid.uuid4().hex[:8]
            # Build prompt with run_id for unique dataset naming
            prompt = build_prompt_func(treatment, name, rep, run_id)
            items.append(WorkItem(
                treatment_name=name, rep=rep, base_dir=str(base_dir), prompt=prompt,
                skills=treatment.skills or {}, claude_md=treatment.claude_md or "",
                noise_tasks=treatment.noise_tasks or [], environment_dir=str(environment_dir),
                timeout=timeout, model=model, files_to_run=files_to_run or None, run_id=run_id,
            ))
    return items
