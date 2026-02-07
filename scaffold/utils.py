"""General utilities for the scaffold framework.

Includes:
- Retry helpers
- Docker helpers
- CLI availability checks
- Model evaluation helpers
"""

import hashlib
import os
import random
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).parent.parent / ".env")


# =============================================================================
# RETRY HELPERS
# =============================================================================

def retry_with_backoff(func, max_retries=3, base_delay=1.0, max_delay=10.0, retry_on=None):
    """Retry a function with exponential backoff and jitter.

    Args:
        func: Callable to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap in seconds
        retry_on: Optional callable(exception) -> bool to determine if retry should happen.
                  If None, retries on rate limit errors (429, "rate limit").

    Returns:
        Result of func() or raises last exception
    """
    if retry_on is None:
        def retry_on(e):
            error_str = str(e).lower()
            return "429" in str(e) or "rate limit" in error_str

    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if not retry_on(e):
                raise
            if attempt < max_retries:
                # Exponential backoff with jitter
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                time.sleep(delay)
    raise last_exception


# =============================================================================
# DOCKER HELPERS
# =============================================================================

DOCKER_IMAGE_PREFIX = "skillbench"


def check_docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_claude_available() -> bool:
    """Check if Claude Code CLI is available."""
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def build_docker_image(test_dir: Path, force: bool = False, verbose: bool = False) -> str | None:
    """Build Docker image from Dockerfile in test directory.

    Uses content-based hashing to avoid rebuilding unchanged images.

    Args:
        test_dir: Directory containing Dockerfile
        force: Force rebuild even if image exists
        verbose: Show build output

    Returns:
        Image name if successful, None otherwise
    """
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


# Common API keys to pass through to Docker
DOCKER_ENV_KEYS = [
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "LANGSMITH_API_KEY", "LANGSMITH_PROJECT",
    "LANGSMITH_TRACING", "LANGSMITH_ENDPOINT",
    "TAVILY_API_KEY"
]


def _build_docker_cmd(
    image_name: str,
    test_dir: Path,
    command: List[str],
    env_vars: Dict[str, str] = None,
) -> List[str]:
    """Build docker run command with common options.

    Internal helper to avoid duplicating docker command building logic.
    """
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{test_dir}:/workspace",
        "-w", "/workspace",
    ]

    # Pass through API keys from environment
    env_vars = env_vars or {}
    for key in DOCKER_ENV_KEYS:
        if key in os.environ and key not in env_vars:
            env_vars[key] = os.environ[key]

    for key, value in env_vars.items():
        docker_cmd.extend(["-e", f"{key}={value}"])

    docker_cmd.append(image_name)
    docker_cmd.extend(command)

    return docker_cmd


def run_in_docker(
    test_dir: Path,
    command: List[str],
    timeout: int = 120,
    env_vars: Dict[str, str] = None,
    image_name: str = None,
) -> subprocess.CompletedProcess:
    """Run a command inside a Docker container.

    Args:
        test_dir: Directory to mount as /workspace
        command: Command to run (e.g., ["python", "script.py", "--arg"])
        timeout: Timeout in seconds
        env_vars: Additional environment variables
        image_name: Docker image (builds from Dockerfile if not provided)

    Returns:
        CompletedProcess with stdout/stderr
    """
    if not image_name:
        image_name = build_docker_image(test_dir)
        if not image_name:
            raise RuntimeError("No Dockerfile or build failed")

    docker_cmd = _build_docker_cmd(image_name, test_dir, command, env_vars)
    return subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)


def run_python_in_docker(
    test_dir: Path,
    script_name: str,
    timeout: int = 120,
    args: List[str] = None,
) -> tuple[bool, str]:
    """Run a Python script in Docker container.

    Convenience wrapper around run_in_docker for Python scripts.

    Args:
        test_dir: Directory containing the script
        script_name: Name of Python script to run
        timeout: Timeout in seconds
        args: Optional arguments to pass to the script

    Returns:
        Tuple of (success: bool, output: str)
    """
    if not check_docker_available():
        return False, "Docker not available"

    command = ["python", script_name]
    if args:
        command.extend(args)

    try:
        result = run_in_docker(test_dir, command, timeout=timeout)
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout}s)"
    except RuntimeError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def run_claude_in_docker(
    test_dir: Path,
    prompt: str,
    timeout: int = 300,
    model: str = None,
) -> subprocess.CompletedProcess:
    """Run Claude Code CLI inside Docker container.

    Args:
        test_dir: Directory to mount as /workspace
        prompt: Prompt to send to Claude
        timeout: Timeout in seconds
        model: Optional model override

    Returns:
        CompletedProcess with stdout/stderr

    Raises:
        RuntimeError: If Docker is not available or image build fails
    """
    if not check_docker_available():
        raise RuntimeError("Docker not available")

    image_name = build_docker_image(test_dir, verbose=False)
    if not image_name:
        raise RuntimeError("Failed to build Docker image")

    command = [
        "claude", "-p", prompt,
        "--dangerously-skip-permissions",
        "--output-format", "stream-json",
        "--verbose",
    ]
    if model:
        command.extend(["--model", model])

    docker_cmd = _build_docker_cmd(image_name, test_dir, command)
    return subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)


# =============================================================================
# PARSING HELPERS
# =============================================================================

def read_json_file(path: Path) -> tuple:
    """Read and parse JSON file.

    Returns:
        (data, None) on success, (None, error_string) on failure
    """
    import json
    if not path.exists():
        return None, f"{path.name} not found"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"


def get_field(obj: dict, *keys, default=None):
    """Get first matching field from dict. Tries keys in order.

    Example:
        get_field({"a": 1}, "b", "a")  # returns 1
        get_field({"x": 1}, "a", "b", default=0)  # returns 0
    """
    for key in keys:
        if key in obj:
            return obj[key]
    return default


def get_nested_field(obj: dict, outer_keys: list, inner_keys: list, default=None):
    """Get field from nested dict, trying multiple key names at each level.

    Example:
        data = {"outputs": {"trajectory": [1,2,3]}}
        get_nested_field(data, ["outputs", "output"], ["trajectory", "traj"])
        # returns [1,2,3]
    """
    outer = get_field(obj, *outer_keys) or {}
    if isinstance(outer, dict):
        return get_field(outer, *inner_keys, default=default)
    return default


def normalize_score(score) -> float:
    """Normalize score to 0-1 range.

    - bool: True->1.0, False->0.0
    - int/float > 1: divide by 100 (assumes percentage)
    - None: returns 0.0
    """
    if isinstance(score, bool):
        return 1.0 if score else 0.0
    if isinstance(score, (int, float)) and score > 1:
        return score / 100.0
    return float(score) if score is not None else 0.0


def extract_score(result: dict):
    """Extract score from result dict, trying common key names.

    Tries: score, key, result, value, match, similarity.
    Falls back to first value if none match.
    """
    if not isinstance(result, dict) or not result:
        return None
    for key in ["score", "key", "result", "value", "match", "similarity"]:
        if key in result:
            return result[key]
    return list(result.values())[0]


# =============================================================================
# MODEL EVALUATION HELPERS
# =============================================================================

class EvalResult(BaseModel):
    """Structured evaluation result."""
    passed: bool = Field(description="Whether the output meets expectations")
    reason: str = Field(description="Brief explanation (max 10 words)")


def get_eval_model(model: str = None, temperature: float = 0):
    """Get an evaluation model using init_chat_model.

    Args:
        model: Model string (e.g., "openai:gpt-4o-mini").
               Defaults to EVAL_MODEL env var or "openai:gpt-4o-mini".
        temperature: Model temperature

    Returns:
        Initialized chat model
    """
    from langchain.chat_models import init_chat_model

    model = model or os.getenv("EVAL_MODEL", "openai:gpt-4o-mini")
    return init_chat_model(model, temperature=temperature)


def evaluate_with_schema(prompt: str, model: str = None) -> dict:
    """Evaluate and return structured result using with_structured_output.

    Args:
        prompt: The evaluation prompt
        model: Optional model override

    Returns:
        Dict with "pass" (bool) and "reason" (str) keys
    """
    try:
        chat_model = get_eval_model(model=model)
        structured_model = chat_model.with_structured_output(EvalResult)
        result = structured_model.invoke(prompt)
        return {"pass": result.passed, "reason": result.reason}
    except Exception as e:
        return {"pass": False, "reason": f"eval error: {str(e)[:30]}"}
