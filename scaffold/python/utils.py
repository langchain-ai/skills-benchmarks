"""Python utilities - thin wrappers around shell scripts.

Shell scripts (scaffold/shell/) are the source of truth.
"""

import json
import os
import random
import subprocess
import time
from pathlib import Path

from dotenv import load_dotenv
from langsmith.run_helpers import tracing_context
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).parent.parent.parent / ".env")

SHELL_DIR = Path(__file__).parent.parent / "shell"


def run_shell(
    script: str, *args, timeout: int = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Run a shell script from scaffold/shell/."""
    cmd = ["bash", str(SHELL_DIR / script)] + [str(a) for a in args]
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, check=check, env=os.environ.copy()
    )


# =============================================================================
# DOCKER (via docker.sh)
# =============================================================================


def check_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        return run_shell("docker.sh", "check", check=False, timeout=10).returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_claude_available() -> bool:
    """Check if Claude CLI is available."""
    try:
        return (
            subprocess.run(["claude", "--version"], capture_output=True, timeout=10).returncode == 0
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def build_docker_image(test_dir: Path, force: bool = False, verbose: bool = False) -> str | None:
    """Build Docker image (cached by Dockerfile hash)."""
    try:
        args = ["build", str(test_dir)] + (["--force"] if force else [])
        result = run_shell("docker.sh", *args, timeout=300, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    except subprocess.TimeoutExpired:
        return None


def run_in_docker(
    test_dir: Path, command: list, timeout: int = 120, env_vars: dict = None, image_name: str = None
) -> subprocess.CompletedProcess:
    """Run command in Docker container."""
    old_env = {k: os.environ.get(k) for k in (env_vars or {})}
    for k, v in (env_vars or {}).items():
        os.environ[k] = v
    try:
        return run_shell("docker.sh", "run", str(test_dir), *command, timeout=timeout, check=False)
    finally:
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def run_python_in_docker(
    test_dir: Path, script_name: str, timeout: int = 120, args: list = None
) -> tuple[bool, str]:
    """Run Python script in Docker. Returns (success, output)."""
    if not check_docker_available():
        return False, "Docker not available"
    try:
        cmd = ["run-python", str(test_dir), script_name] + (args or [])
        result = run_shell("docker.sh", *cmd, timeout=timeout, check=False)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout}s)"
    except Exception as e:
        return False, str(e)


def run_node_in_docker(
    test_dir: Path, script_name: str, timeout: int = 120, args: list = None
) -> tuple[bool, str]:
    """Run Node.js/TypeScript script in Docker. Returns (success, output)."""
    if not check_docker_available():
        return False, "Docker not available"
    try:
        cmd = ["run-node", str(test_dir), script_name] + (args or [])
        result = run_shell("docker.sh", *cmd, timeout=timeout, check=False)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout}s)"
    except Exception as e:
        return False, str(e)


def run_claude_in_docker(
    test_dir: Path, prompt: str, timeout: int = 300, model: str = None
) -> subprocess.CompletedProcess:
    """Run Claude CLI in Docker container."""
    if not check_docker_available():
        raise RuntimeError("Docker not available")
    cmd = ["run-claude", str(test_dir), prompt, "--timeout", str(timeout)]
    if model:
        cmd.extend(["--model", model])
    try:
        return run_shell("docker.sh", *cmd, timeout=timeout + 30, check=False)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", f"Timeout after {timeout}s")


def setup_langsmith_hook(test_dir: Path, project: str = "claude-code-benchmark") -> bool:
    """Set up LangSmith tracing hook for Claude Code."""
    try:
        run_shell("setup.sh", "setup-langsmith-hook", str(test_dir), project)
        return True
    except subprocess.CalledProcessError:
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


def read_json_file(path: Path) -> tuple:
    """Read JSON file. Returns (data, None) or (None, error)."""
    if not path.exists():
        return None, f"{path.name} not found"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"


def get_field(obj: dict, *keys, default=None):
    """Get first matching field from dict."""
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
        return None, f"{skip_msg} ({str(e)[:40]})"


# =============================================================================
# LLM EVALUATION
# =============================================================================


def get_eval_model(model: str = None, temperature: float = 0):
    """Get evaluation model."""
    from langchain.chat_models import init_chat_model

    return init_chat_model(
        model or os.getenv("EVAL_MODEL", "openai:gpt-4o-mini"), temperature=temperature
    )


class EvalResult(BaseModel):
    """Structured output for LLM-based evaluation."""

    passed: bool = Field(description="Whether output meets expectations")
    reason: str = Field(description="Brief explanation")


def evaluate_with_schema(prompt: str, model: str = None) -> dict:
    """Evaluate with structured output. Returns {"pass": bool, "reason": str}."""
    try:
        # Detach from parent trace context (e.g. ls_test) so evaluator traces
        # go to "skills-validation" instead of inheriting the experiment project.
        with tracing_context(project_name="skills-validation", parent=False):
            result = get_eval_model(model).with_structured_output(EvalResult).invoke(prompt)
        return {"pass": result.passed, "reason": result.reason}
    except Exception as e:
        return {"pass": False, "reason": f"eval error: {str(e)[:30]}"}
