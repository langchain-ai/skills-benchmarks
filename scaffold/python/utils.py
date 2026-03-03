"""Python utilities - thin wrappers around shell scripts.

Shell scripts (scaffold/shell/) are the source of truth.
"""

import json
import os
import random
import shutil
import subprocess
import time
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Reserved filenames for host ↔ Docker data transport.
# Duplicated from validation/core.py (can't import due to circular dependency via __init__.py).
TEST_CONTEXT_FILE = os.environ.get("BENCH_TEST_CONTEXT", "_test_context.json")
TEST_RESULTS_FILE = os.environ.get("BENCH_TEST_RESULTS", "_test_results.json")

load_dotenv(Path(__file__).parent.parent.parent / ".env")

SHELL_DIR = Path(__file__).parent.parent / "shell"
SCAFFOLD_PYTHON_DIR = Path(__file__).parent


def run_shell(
    script: str, *args, timeout: int = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Run a shell script from scaffold/shell/."""
    cmd = ["bash", str(SHELL_DIR / script)] + [str(a) for a in args]
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, check=check, env=os.environ.copy()
    )


# =============================================================================
# DOCKER: Low-level (thin wrappers around docker.sh)
# =============================================================================


def check_docker_available() -> bool:
    """Check if Docker daemon is reachable."""
    try:
        return run_shell("docker.sh", "check", check=False, timeout=10).returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def build_docker_image(test_dir: Path, force: bool = False, verbose: bool = False) -> str | None:
    """Build Docker image for test_dir (cached by build context hash). Returns image name or None."""
    try:
        args = ["build", str(test_dir)] + (["--force"] if force else [])
        result = run_shell("docker.sh", *args, timeout=300, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    except subprocess.TimeoutExpired:
        return None


def _docker_run_script(
    mode: str, test_dir: Path, script_name: str, timeout: int = 120, args: list = None
) -> tuple[bool, str]:
    """Run a script in Docker. Returns (success, stdout).

    Args:
        mode: docker.sh subcommand ("run-python" or "run-node")
    """
    if not check_docker_available():
        return False, "Docker not available"
    try:
        cmd = [mode, str(test_dir), script_name] + (args or [])
        result = run_shell("docker.sh", *cmd, timeout=timeout, check=False)
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout}s)"
    except Exception as e:
        return False, str(e)


def run_python_in_docker(
    test_dir: Path, script_name: str, timeout: int = 120, args: list = None
) -> tuple[bool, str]:
    """Run Python script in Docker. Returns (success, output)."""
    return _docker_run_script("run-python", test_dir, script_name, timeout, args)


def run_node_in_docker(
    test_dir: Path, script_name: str, timeout: int = 120, args: list = None
) -> tuple[bool, str]:
    """Run Node.js/TypeScript script in Docker. Returns (success, output)."""
    return _docker_run_script("run-node", test_dir, script_name, timeout, args)


def run_claude_in_docker(
    test_dir: Path, prompt: str, timeout: int = 300, model: str = None
) -> subprocess.CompletedProcess:
    """Run Claude CLI in Docker. Returns CompletedProcess."""
    if not check_docker_available():
        raise RuntimeError("Docker not available")
    cmd = ["run-claude", str(test_dir), prompt, "--timeout", str(timeout)]
    if model:
        cmd.extend(["--model", model])
    try:
        return run_shell("docker.sh", *cmd, timeout=timeout + 30, check=False)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", f"Timeout after {timeout}s")


# =============================================================================
# DOCKER: Eval orchestration (copy files → run test → parse JSON)
# =============================================================================


def _copy_scaffold_to_docker(test_dir: Path):
    """Copy both Python and TypeScript scaffolds into test_dir.

    Test scripts may be in either language regardless of which test runner
    invokes them, so both scaffolds are always available.
    """
    scaffold_root = SCAFFOLD_PYTHON_DIR.parent
    scaffold_dir = test_dir / "scaffold"
    scaffold_dir.mkdir(parents=True, exist_ok=True)
    (scaffold_dir / "__init__.py").touch()

    # Python scaffold
    py_dest = scaffold_dir / "python"
    py_dest.mkdir(exist_ok=True)
    (py_dest / "__init__.py").touch()
    shutil.copy(SCAFFOLD_PYTHON_DIR / "utils.py", py_dest / "utils.py")
    py_validation = SCAFFOLD_PYTHON_DIR / "validation"
    if py_validation.is_dir():
        shutil.copytree(py_validation, py_dest / "validation", dirs_exist_ok=True)

    # TypeScript scaffold (so TS test scripts work from Python runner too)
    ts_src = scaffold_root / "typescript"
    if ts_src.is_dir():
        ts_dest = scaffold_dir / "typescript"
        ts_dest.mkdir(parents=True, exist_ok=True)
        ts_utils = ts_src / "utils.ts"
        if ts_utils.exists():
            shutil.copy(ts_utils, ts_dest / "utils.ts")
        ts_validation = ts_src / "validation"
        if ts_validation.is_dir():
            shutil.copytree(ts_validation, ts_dest / "validation", dirs_exist_ok=True)


def _parse_json_output(output: str) -> dict | None:
    """Extract a JSON dict from command output (handles pretty-printed and single-line).

    Robust to extra output before/after the JSON (e.g., Docker build logs,
    warnings, print statements). Finds the last { ... } block in the output.
    """
    stripped = output.strip()
    # Try full output first (clean JSON)
    try:
        result = json.loads(stripped)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError):
        pass
    # Find the last top-level JSON object in the output
    # by scanning backwards for the last '}'  and matching '{'
    last_brace = stripped.rfind("}")
    if last_brace >= 0:
        # Find the matching opening brace
        depth = 0
        for i in range(last_brace, -1, -1):
            if stripped[i] == "}":
                depth += 1
            elif stripped[i] == "{":
                depth -= 1
            if depth == 0:
                try:
                    result = json.loads(stripped[i : last_brace + 1])
                    if isinstance(result, dict):
                        return result
                except (json.JSONDecodeError, ValueError):
                    break
    # Fall back to last JSON line (single-line output)
    for line in reversed(stripped.splitlines()):
        try:
            result = json.loads(line)
            if isinstance(result, dict):
                return result
        except (json.JSONDecodeError, ValueError):
            continue
    return None


def run_eval_in_docker(
    test_dir: Path,
    validation_dir: Path,
    test_script: str,
    timeout: int = 120,
    data_dir: Path | None = None,
) -> dict:
    """Copy files into test_dir, run test script in Docker, return parsed JSON results.

    Copies into test_dir (mirroring the local task directory structure):
    - validation/ — test scripts and helpers
    - data/ — ground truth, test cases, reference files
    - scaffold/python/validation/ package (so test scripts can import helpers)

    Test scripts read artifacts and run context from _test_context.json.
    """
    # Copy into subdirectories matching the task's local structure so paths
    # are consistent between local development and Docker execution.
    val_dir = test_dir / "validation"
    val_dir.mkdir(exist_ok=True)
    for f in validation_dir.iterdir():
        if f.is_file():
            shutil.copy(f, val_dir / f.name)
    if data_dir and data_dir.is_dir():
        dest_data = test_dir / "data"
        dest_data.mkdir(exist_ok=True)
        for f in data_dir.iterdir():
            if f.is_file():
                shutil.copy(f, dest_data / f.name)
    _copy_scaffold_to_docker(test_dir)
    # Remove stale results file from a previous script run
    results_path = test_dir / TEST_RESULTS_FILE
    results_path.unlink(missing_ok=True)
    script_path = f"validation/{test_script}"
    if test_script.endswith((".ts", ".js")):
        success, output = run_node_in_docker(test_dir, script_path, timeout=timeout)
    else:
        success, output = run_python_in_docker(test_dir, script_path, timeout=timeout)
    # Primary: read results from file (immune to stdout pollution)
    if results_path.exists():
        try:
            return json.loads(results_path.read_text())
        except (json.JSONDecodeError, ValueError):
            pass
    # Fallback: parse stdout
    result = _parse_json_output(output)
    if result is not None:
        return result
    return {"error": f"No JSON output. success={success}, output={output[:300]}"}


_EVAL_TRACE_KEYS = ["BENCH_EVAL_LANGSMITH_TRACE", "BENCH_EVAL_BAGGAGE"]


def _set_eval_trace_env() -> list[str]:
    """Set env vars so Docker eval scripts can nest traces under the current span.

    Uses LangSmith distributed tracing headers (langsmith-trace + baggage).
    Returns list of env var keys that were set (for cleanup).
    """
    from langsmith.run_helpers import get_current_run_tree

    run_tree = get_current_run_tree()
    if not run_tree:
        return []

    headers = run_tree.to_headers()
    set_keys = []
    if headers.get("langsmith-trace"):
        os.environ["BENCH_EVAL_LANGSMITH_TRACE"] = headers["langsmith-trace"]
        set_keys.append("BENCH_EVAL_LANGSMITH_TRACE")
    if headers.get("baggage"):
        os.environ["BENCH_EVAL_BAGGAGE"] = headers["baggage"]
        set_keys.append("BENCH_EVAL_BAGGAGE")
    return set_keys


def make_execution_validator(
    validation_dir: Path,
    test_scripts: str | list[str],
    target_artifacts: str | list[str],
    timeout: int = 120,
    data_dir: Path | None = None,
):
    """Create a validator that runs test script(s) in Docker.

    This is the standard way to build validators. Write a test script that
    outputs {"passed": [...], "failed": [...]} JSON, then wire it up:

        validate_execution = make_execution_validator(
            validation_dir=Path(__file__).parent,
            test_scripts="test_memory.py",
            target_artifacts="agent_system.py",
        )

    Args:
        validation_dir: Directory containing test scripts (typically Path(__file__).parent).
        test_scripts: Name(s) of test script(s) to run. Results are aggregated.
        target_artifacts: File(s) or directory(s) Claude should produce. All are
            checked for existence and passed as args to each test script.
        timeout: Docker execution timeout in seconds.
        data_dir: Optional directory with ground truth / test case data to copy.
    """
    test_scripts = [test_scripts] if isinstance(test_scripts, str) else test_scripts
    artifacts = [target_artifacts] if isinstance(target_artifacts, str) else target_artifacts

    def validate_execution(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
        from langsmith.run_helpers import trace as ls_trace

        passed, failed = [], []
        with ls_trace(
            name="check_artifacts",
            inputs={"artifacts": artifacts},
        ) as artifacts_run:
            for artifact in artifacts:
                # Support glob patterns (e.g., "backend/evaluator.*")
                if any(c in artifact for c in "*?["):
                    if not list(test_dir.glob(artifact)):
                        failed.append(f"Artifact not found: {artifact}")
                elif not (test_dir / artifact).exists():
                    failed.append(f"Artifact not found: {artifact}")
            if artifacts_run:
                artifacts_run.outputs = {"passed": not failed, "missing": failed}
        if failed:
            return passed, failed
        # Serialize run context + target artifacts for test scripts
        context = dict(outputs) if outputs else {}
        context["target_artifacts"] = artifacts
        (test_dir / TEST_CONTEXT_FILE).write_text(json.dumps(context, default=str))
        eval_trace_keys = []
        for script in test_scripts:
            with ls_trace(
                name=f"eval_{script}",
                inputs={"script": script, "artifacts": artifacts},
            ) as eval_run:
                # Pass trace context to Docker so LLM calls (e.g. evaluate_with_schema)
                # nest under this eval span
                eval_trace_keys = _set_eval_trace_env()
                try:
                    results = run_eval_in_docker(
                        test_dir,
                        validation_dir,
                        script,
                        timeout=timeout,
                        data_dir=data_dir,
                    )
                finally:
                    for key in eval_trace_keys:
                        os.environ.pop(key, None)
                passed.extend(results.get("passed", []))
                failed.extend(results.get("failed", []))
                if results.get("error") and not results.get("passed") and not results.get("failed"):
                    failed.append(f"Test execution error ({script}): {results['error']}")
                if eval_run:
                    eval_run.outputs = {
                        "passed": results.get("passed", []),
                        "failed": results.get("failed", []),
                        "error": results.get("error"),
                    }
        return passed, failed

    return validate_execution


# =============================================================================
# ENVIRONMENT CHECKS & SETUP
# =============================================================================


def check_claude_available() -> bool:
    """Check if Claude CLI is installed."""
    try:
        return (
            subprocess.run(["claude", "--version"], capture_output=True, timeout=10).returncode == 0
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# =============================================================================
# HELPERS
# =============================================================================


def retry_with_backoff(func, max_retries=3, base_delay=1.0, max_delay=10.0, retry_on=None):
    """Retry with exponential backoff."""
    retry_on = retry_on or (lambda e: "429" in str(e) or "rate limit" in str(e).lower())
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exc = e
            if not retry_on(e) or attempt == max_retries:
                raise
            time.sleep(min(base_delay * (2**attempt) + random.uniform(0, 1), max_delay))
    raise last_exc


def read_json_file(path: Path) -> tuple[dict | list | None, str | None]:
    """Read JSON file. Returns (data, None) or (None, error)."""
    if not path.exists():
        return None, f"file not found: {path.name}"
    try:
        with open(path) as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"
    except Exception as e:
        return None, str(e)


def get_field(obj, *keys, default=None):
    """Get first matching field from dict."""
    if not isinstance(obj, dict):
        return default
    for key in keys:
        if key in obj:
            return obj[key]
    return default


def get_nested_field(obj: dict, outer_keys: list, inner_keys: list, default=None):
    """Get field from nested dict."""
    outer = get_field(obj, *outer_keys) or {}
    return get_field(outer, *inner_keys, default=default) if isinstance(outer, dict) else default


def normalize_score(score) -> float:
    """Normalize score to 0-1 range."""
    if isinstance(score, bool):
        return 1.0 if score else 0.0
    if isinstance(score, (int, float)) and score > 1:
        return score / 100.0
    return float(score) if score is not None else 0.0


# =============================================================================
# LANGSMITH CLIENT
# =============================================================================


def get_langsmith_client():
    """Get LangSmith client. Returns (client, error_string).

    Returns:
        Tuple of (Client instance or None, error message or None)
    """
    try:
        from langsmith import Client

        api_key = os.environ.get("LANGSMITH_API_KEY")
        if not api_key:
            return None, "LANGSMITH_API_KEY not set"
        return Client(api_key=api_key), None
    except Exception as e:
        return None, str(e)


def safe_api_call(func, skip_msg: str = "skipped"):
    """Run API call, return (result, error_msg) handling rate limits.

    Args:
        func: Function to call
        skip_msg: Message prefix for skip/error cases

    Returns:
        Tuple of (result or None, error message or None)
    """
    try:
        return func(), None
    except Exception as e:
        msg = str(e).lower()
        if "429" in msg or "rate limit" in msg:
            return None, f"{skip_msg} (rate limited)"
        return None, f"{skip_msg} ({str(e)[:100]})"


# =============================================================================
# LLM EVALUATION
# =============================================================================


def get_eval_model(model: str = None, temperature: float = 0):
    """Get evaluation model."""
    from langchain.chat_models import init_chat_model

    return init_chat_model(
        model or os.getenv("BENCH_EVAL_MODEL", "openai:gpt-4o-mini"), temperature=temperature
    )


class EvalResult(BaseModel):
    """Structured output for LLM-based evaluation."""

    passed: bool = Field(description="Whether output meets expectations")
    reason: str = Field(description="Brief explanation")


def evaluate_with_schema(prompt: str, model: str = None) -> dict:
    """Evaluate with structured output. Returns {"pass": bool, "reason": str}."""
    try:
        result = (
            get_eval_model(model)
            .with_structured_output(EvalResult, method="json_mode")
            .invoke(
                [
                    {
                        "role": "system",
                        "content": 'Evaluate the output. Respond as JSON: {"passed": bool, "reason": "..."}',
                    },
                    {"role": "user", "content": prompt},
                ]
            )
        )
        return {"pass": result.passed, "reason": result.reason}
    except Exception as e:
        return {"pass": False, "reason": f"eval error: {str(e)[:30]}"}
