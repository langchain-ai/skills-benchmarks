"""Test runner for Claude Code CLI."""

import os
import json
import subprocess
import hashlib
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Callable
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"


# =============================================================================
# LOGGING
# =============================================================================

def log(message: str, level: str = "INFO"):
    """Print timestamped log message."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {message}")


def save_log(content: str, log_dir: Path, name: str, suffix: str = "") -> Path:
    """Save content to log file."""
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = name.replace(" ", "_").replace("/", "_").lower()
    filename = f"{safe}_{ts}{suffix}"
    path = log_dir / filename
    path.write_text(content)
    return path


# =============================================================================
# OUTPUT PARSING
# =============================================================================

def parse_output(stdout: str) -> Dict[str, Any]:
    """Parse stream-json output into structured data."""
    if not stdout:
        return {"messages": []}
    messages = []
    for line in stdout.strip().split('\n'):
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return {"messages": messages}


def extract_events(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Extract events (tool calls, files, etc.) from parsed output."""
    events = {
        "tool_calls": [], "files_read": [], "files_created": [],
        "files_modified": [], "commands_run": [], "skills_invoked": [],
        "duration_seconds": None, "num_turns": None,
    }

    for msg in parsed.get("messages", []):
        if msg.get("type") == "result":
            events["duration_seconds"] = msg.get("duration_ms", 0) / 1000
            events["num_turns"] = msg.get("num_turns")

        if msg.get("type") == "assistant":
            for item in msg.get("message", {}).get("content", []):
                if item.get("type") == "tool_use":
                    tool, inp = item.get("name", ""), item.get("input", {})
                    events["tool_calls"].append({"tool": tool, "input": inp})
                    path = inp.get("file_path", "")
                    if tool == "Read" and path:
                        events["files_read"].append(path)
                    elif tool == "Write" and path:
                        events["files_created"].append(path)
                    elif tool == "Edit" and path:
                        events["files_modified"].append(path)
                    elif tool == "Bash" and inp.get("command"):
                        events["commands_run"].append(inp["command"])
                    elif tool == "Skill" and inp.get("skill"):
                        events["skills_invoked"].append(inp["skill"])
    return events


def save_events(events: Dict[str, Any], output_dir: Path, name: str) -> Path:
    """Save events to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = name.replace(" ", "_").replace("/", "_").lower()
    path = output_dir / f"{safe}_{ts}.json"
    path.write_text(json.dumps(events, indent=2))
    return path


# =============================================================================
# DOCKER
# =============================================================================

DOCKER_IMAGE_PREFIX = "skillbench"


def check_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


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
            log(f"Using cached Docker image: {image_name}")
            return image_name

    log(f"Building Docker image {image_name}...")

    # Build with output visible if verbose
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
        log(f"Docker image built: {image_name}")
        return image_name
    else:
        stderr = getattr(result, 'stderr', 'See output above')
        log(f"Docker build failed: {stderr[:200] if stderr else 'unknown error'}")
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
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LANGSMITH_API_KEY"]:
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

    log(f"Running {script_name} in Docker...")
    try:
        result = run_in_docker(image_name, test_dir, ["python", script_name], timeout=timeout)
        output = result.stdout + result.stderr
        status = "success" if result.returncode == 0 else "failed"
        log(f"Docker run {status}: {len(output)} chars output")
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        log(f"Docker run timeout: {timeout}s")
        return False, f"Timeout ({timeout}s)"
    except Exception as e:
        log(f"Docker run error: {e}")
        return False, str(e)


# =============================================================================
# TEST RUNNER
# =============================================================================

@dataclass
class TestResult:
    name: str
    passed: bool
    checks_passed: List[str]
    checks_failed: List[str]
    events: Dict[str, Any]


def run_test(
    name: str,
    prompt: str,
    test_dir: Path,
    validate: Callable[[Dict, Path], tuple[List[str], List[str]]],
    timeout: int = 300,
    model: str = None,
    save: bool = True,
) -> TestResult:
    """Run Claude Code CLI, validate results, return TestResult."""
    log(f"Starting test: {name}")
    log(f"Test directory: {test_dir}")

    # Run Claude Code
    cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions",
           "--output-format", "stream-json", "--verbose"]
    if model:
        cmd.extend(["--model", model])

    log(f"Running Claude Code CLI (timeout: {timeout}s)...")
    start_time = datetime.now()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=timeout, cwd=str(test_dir), env=os.environ.copy())
        duration = (datetime.now() - start_time).total_seconds()
        log(f"Claude completed in {duration:.1f}s")

        # Save raw output
        if save:
            raw_log_dir = LOGS_DIR / "raw"
            save_log(result.stdout, raw_log_dir, name, "_stdout.json")
            if result.stderr:
                save_log(result.stderr, raw_log_dir, name, "_stderr.txt")

        events = extract_events(parse_output(result.stdout))
        log(f"Extracted {len(events.get('tool_calls', []))} tool calls, "
            f"{len(events.get('files_created', []))} files created")

    except subprocess.TimeoutExpired:
        log(f"TIMEOUT after {timeout}s")
        return TestResult(name, False, [], [f"Timeout after {timeout}s"], {})

    # Save events
    if save:
        events_path = save_events(events, LOGS_DIR / "events", name)
        log(f"Events saved to: {events_path.name}")

    # Validate
    log("Running validation...")
    passed, failed = validate(events, test_dir)
    ok = len(failed) == 0

    # Print results
    status = "PASS" if ok else "FAIL"
    log(f"Result: {status} ({len(passed)} passed, {len(failed)} failed)")

    if passed:
        for p in passed[:5]:  # Show first 5 passes
            print(f"  ✓ {p}")
        if len(passed) > 5:
            print(f"  ... and {len(passed) - 5} more")

    if failed:
        for f in failed:
            print(f"  ✗ {f}")

    # Save report
    if save:
        report = {
            "name": name,
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
        report_path = save_log(json.dumps(report, indent=2), LOGS_DIR / "reports", name, "_report.json")
        log(f"Report saved to: {report_path.name}")

    return TestResult(name, ok, passed, failed, events)
