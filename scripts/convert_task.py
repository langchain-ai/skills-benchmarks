#!/usr/bin/env python3
"""Convert a skills-benchmarks task into a Harbor task directory.

Usage:
    uv run python scripts/convert_task.py oss-fix-lc-streaming
    uv run python scripts/convert_task.py ls-multiskill-basic --out harbor_tasks

What it emits (Harbor schema_version 1.3):
    <out>/<task>/task.toml
    <out>/<task>/instruction.md          # copied verbatim (placeholders left for sweep.py)
    <out>/<task>/environment/            # Dockerfile (+ seed COPY) + workspace seed files
    <out>/<task>/tests/test.sh           # runs ported checks, writes /logs/verifier/reward.txt
    <out>/<task>/tests/<test_*.py>       # ported validation scripts (unchanged)
    <out>/<task>/tests/scaffold/...      # TestRunner + core helpers
    <out>/<task>/tests/_test_context.json
    <out>/<task>/tests/data/             # static reference data (ls-* tasks only)
    <out>/<task>/solution/solve.sh       # oracle: drop the known-good artifact in place

ls-* tasks (those with a [template] section in task.toml) get extra treatment:
    - All scaffold validation modules copied (dataset, tracing, evaluator, scripts)
    - Real get_langsmith_client wired into utils.py; Docker helpers stubbed out
    - LANGSMITH_API_KEY forwarded to both agent and verifier via task.toml env sections
    - test.sh injects $RUN_ID (set by sweep.py via --ve) into _test_context.json
    - Static data/*.json files copied to tests/data/ for reference by validators
"""

import argparse
import json
import re
import shutil
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "tasks"
SCAFFOLD_VALIDATION = REPO_ROOT / "scaffold" / "python" / "validation"

HARBOR_NAMESPACE = "skillbench"
DEFAULT_WORKDIR = "/workspace"


def _toml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _toml_list(values: list[str]) -> str:
    return "[" + ", ".join(_toml_str(v) for v in values) + "]"


def _as_list(value) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def _detect_workdir(dockerfile: str) -> str:
    matches = re.findall(r"^\s*WORKDIR\s+(\S+)", dockerfile, re.MULTILINE)
    return matches[-1] if matches else DEFAULT_WORKDIR


def _detect_user(dockerfile: str) -> str | None:
    matches = re.findall(r"^\s*USER\s+(\S+)", dockerfile, re.MULTILINE)
    return matches[-1] if matches else None


def _strip_benchuser(dockerfile: str) -> str:
    """Remove USER benchuser and its useradd setup from a Dockerfile.

    Harbor's exec_as_agent runs without an explicit user, so it falls back to
    the container's default. If that's benchuser, Harbor's root-chowned venv
    dirs become unwritable. Running as root avoids the conflict.
    """
    out = []
    for line in dockerfile.splitlines():
        stripped = line.strip()
        if stripped == "USER benchuser":
            continue
        if re.match(r"RUN useradd\b.*benchuser", stripped):
            continue
        if stripped == "# Create non-root user for security":
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


_UTILS_STUB = '''\
"""Stub for scaffold.python.utils — LLM-based eval helpers not available in Harbor verifier."""


def evaluate_with_schema(prompt: str, model: str = None) -> dict:
    """No-op stub: LLM eval is informational only and skipped in Harbor."""
    return {"pass": True, "reason": "LLM eval skipped in Harbor verifier"}
'''

# For ls-* tasks: real LangSmith client + stubbed Docker helpers.
_UTILS_LANGSMITH = '''\
"""scaffold.python.utils for Harbor verifier — real LangSmith client, stubbed Docker."""

import json
import os
from pathlib import Path


def evaluate_with_schema(prompt: str, model: str = None) -> dict:
    """No-op stub: LLM eval is informational only and skipped in Harbor."""
    return {"pass": True, "reason": "LLM eval skipped in Harbor verifier"}


def run_python_in_docker(*args, **kwargs):
    """Stub: Docker-in-Docker not available in Harbor verifier."""
    return True, ""


def run_node_in_docker(*args, **kwargs):
    """Stub: Docker-in-Docker not available in Harbor verifier."""
    return True, ""


def check_docker_available() -> bool:
    return False


def get_langsmith_client():
    """Return (Client, None) or (None, error_str)."""
    try:
        from langsmith import Client
        api_key = os.environ.get("LANGSMITH_API_KEY")
        if not api_key:
            return None, "LANGSMITH_API_KEY not set"
        return Client(api_key=api_key), None
    except Exception as e:
        return None, str(e)


def safe_api_call(func, skip_msg: str = "skipped"):
    """Run API call, return (result, error_msg)."""
    try:
        return func(), None
    except Exception as e:
        msg = str(e).lower()
        if "429" in msg or "rate limit" in msg:
            return None, f"{skip_msg} (rate limited)"
        return None, f"{skip_msg}: {str(e)[:80]}"


def read_json_file(path: Path):
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
    if isinstance(score, bool):
        return 1.0 if score else 0.0
    if isinstance(score, (int, float)) and score > 1:
        return score / 100.0
    return float(score) if score is not None else 0.0
'''


# Validation modules to copy for ls-* tasks (need LangSmith validators).
_LS_VALIDATION_MODULES = (
    "runner.py",
    "core.py",
    "dataset.py",
    "tracing.py",
    "evaluator.py",
    "scripts.py",
)


def _copy_scaffold(tests_dir: Path, *, langsmith: bool = False) -> None:
    """Copy the TestRunner + core helpers so ported checks import unchanged."""
    dest = tests_dir / "scaffold" / "python" / "validation"
    dest.mkdir(parents=True, exist_ok=True)
    for level in (tests_dir / "scaffold", tests_dir / "scaffold" / "python", dest):
        (level / "__init__.py").write_text("")
    modules = _LS_VALIDATION_MODULES if langsmith else ("runner.py", "core.py")
    for name in modules:
        src = SCAFFOLD_VALIDATION / name
        if src.exists():
            shutil.copy(src, dest / name)
    utils_content = _UTILS_LANGSMITH if langsmith else _UTILS_STUB
    (tests_dir / "scaffold" / "python" / "utils.py").write_text(utils_content)


def _build_task_toml(
    name: str,
    cfg: dict,
    workdir: str,
    verifier_user: str,
    verifier_env: dict[str, str] | None = None,
    agent_env: dict[str, str] | None = None,
) -> str:
    meta = cfg.get("metadata", {})
    env = cfg.get("environment", {})
    val = cfg.get("validation", {})

    lines = [
        'schema_version = "1.3"',
        "",
        "[task]",
        f"name = {_toml_str(f'{HARBOR_NAMESPACE}/{name}')}",
        f"description = {_toml_str(meta.get('description', ''))}",
        "",
        "[metadata]",
        f"source_task = {_toml_str(name)}",
    ]
    for key in ("difficulty", "category"):
        if key in meta:
            lines.append(f"{key} = {_toml_str(meta[key])}")
    if meta.get("tags"):
        lines.append(f"tags = {_toml_list(_as_list(meta['tags']))}")
    lines += [
        "",
        "[agent]",
        f"timeout_sec = {float(env.get('timeout_sec', 600))}",
        "",
        "[verifier]",
        f"timeout_sec = {float(val.get('timeout', 120))}",
        f"user = {_toml_str(verifier_user)}",
    ]
    if verifier_env:
        lines.append("")
        lines.append("[verifier.env]")
        for k, v in verifier_env.items():
            lines.append(f"{k} = {_toml_str(v)}")
    lines += [
        "",
        "[environment]",
        "build_timeout_sec = 1800.0",
        f"workdir = {_toml_str(workdir)}",
        # Size the LangSmith snapshot builder; the default is too small to build
        # the full LangChain/LangGraph image. Ignored/harmless for docker.
        "cpus = 4",
        "memory_mb = 8192",
        "storage_mb = 65536",
        '# skills_dir = "skills"  # Phase 1: per-treatment skills copied to the agent skills config dir',
    ]
    if agent_env:
        lines.append("")
        lines.append("[environment.env]")
        for k, v in agent_env.items():
            lines.append(f"{k} = {_toml_str(v)}")
    lines.append("")
    return "\n".join(lines)


def convert(task_name: str, out_root: Path) -> Path:
    src = TASKS_DIR / task_name
    if not src.is_dir():
        sys.exit(f"Task not found: {src}")
    cfg = tomllib.loads((src / "task.toml").read_text())

    val = cfg.get("validation", {})
    target_artifacts = _as_list(val.get("target_artifacts"))
    test_scripts = _as_list(val.get("test_scripts"))
    if not target_artifacts or not test_scripts:
        sys.exit(f"{task_name}: task.toml [validation] needs target_artifacts and test_scripts")

    # ls-* tasks have a [template] section and need LangSmith wiring.
    is_ls_task = "template" in cfg

    dockerfile = _strip_benchuser((src / "environment" / "Dockerfile").read_text())
    workdir = _detect_workdir(dockerfile)
    image_user = _detect_user(dockerfile)
    # The verifier writes to the Harbor-mounted /logs/verifier; run it as root
    # so it can write there regardless of the image's default USER.
    verifier_user = "root"

    verifier_env = {"LANGSMITH_API_KEY": "${LANGSMITH_API_KEY}"} if is_ls_task else None
    agent_env = {"LANGSMITH_API_KEY": "${LANGSMITH_API_KEY}"} if is_ls_task else None

    out = out_root / task_name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # task.toml + instruction
    _write(
        out / "task.toml",
        _build_task_toml(task_name, cfg, workdir, verifier_user, verifier_env, agent_env),
    )
    shutil.copy(src / "instruction.md", out / "instruction.md")

    # environment: copy all build-context files, then append COPY for seed artifacts
    env_out = out / "environment"
    env_out.mkdir()
    for f in (src / "environment").iterdir():
        if f.is_file():
            shutil.copy(f, env_out / f.name)
        elif f.is_dir():
            shutil.copytree(f, env_out / f.name)
    seed_copies = []
    chown = f"--chown={image_user}:{image_user} " if image_user else ""
    for artifact in target_artifacts:
        # Only seed artifacts that are files (not directory targets like "backend")
        if (env_out / artifact).is_file():
            seed_copies.append(f"COPY {chown}{artifact} {workdir}/{artifact}")
    if seed_copies:
        extra = "\n# [skillbench-harbor] seed the agent workspace with starting files\n"
        extra += "\n".join(seed_copies) + "\n"
        (env_out / "Dockerfile").write_text(dockerfile.rstrip() + "\n" + extra)
    else:
        (env_out / "Dockerfile").write_text(dockerfile)

    # tests: ported scripts + scaffold + context + test.sh
    tests_out = out / "tests"
    tests_out.mkdir()
    for script in test_scripts:
        shutil.copy(src / "validation" / script, tests_out / script)
    _copy_scaffold(tests_out, langsmith=is_ls_task)

    # ls-* tasks: copy static reference data (*.json but not *.jsonl trace files)
    if is_ls_task and (src / "data").is_dir():
        data_out = tests_out / "data"
        data_out.mkdir()
        for f in (src / "data").iterdir():
            if f.is_file() and f.suffix == ".json":
                shutil.copy(f, data_out / f.name)

    _write(
        tests_out / "_test_context.json",
        json.dumps({"target_artifacts": target_artifacts}, indent=2),
    )
    _write(tests_out / "test.sh", _build_test_sh(test_scripts, workdir, inject_run_id=is_ls_task))

    # solution: oracle drops the known-good artifact(s) into the workspace
    sol_out = out / "solution"
    sol_out.mkdir()
    oracle_files = _collect_oracle(src, target_artifacts, sol_out)
    _write(sol_out / "solve.sh", _build_solve_sh(oracle_files, workdir))

    return out


def _build_test_sh(test_scripts: list[str], workdir: str, *, inject_run_id: bool = False) -> str:
    runs = "\n".join(f"python /tests/{s}\nstatus=$((status | $?))" for s in test_scripts)
    # ls-* tasks: sweep.py passes RUN_ID via --ve; inject it into _test_context.json
    # so validators can scope LangSmith queries to this specific run.
    run_id_block = (
        """
# Inject RUN_ID into test context so validators can scope LangSmith queries.
if [ -n "${RUN_ID:-}" ]; then
  python3 -c "
import json, sys
path = '/tests/_test_context.json'
with open(path) as f:
    ctx = json.load(f)
ctx['run_id'] = sys.argv[1]
with open(path, 'w') as f:
    json.dump(ctx, f, indent=2)
" "$RUN_ID"
fi
"""
        if inject_run_id
        else ""
    )
    return f"""#!/usr/bin/env bash
# Run the ported validation checks and translate the result into a Harbor reward.
set -uo pipefail

export BENCH_TEST_CONTEXT="/tests/_test_context.json"
export BENCH_TEST_RESULTS="/logs/verifier/_test_results.json"
mkdir -p /logs/verifier

cd "{workdir}" || exit 1
export PYTHONPATH="/tests:${{PYTHONPATH:-}}"
{run_id_block}
status=0
{runs}

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
"""


def _collect_oracle(src: Path, target_artifacts: list[str], sol_out: Path) -> list[str]:
    """Copy known-good artifacts from the task's data/ dir into solution/.

    Looks for data/fixed_<artifact> then data/<artifact>.
    """
    data = src / "data"
    copied = []
    for artifact in target_artifacts:
        for candidate in (data / f"fixed_{artifact}", data / artifact):
            if candidate.is_file():
                shutil.copy(candidate, sol_out / artifact)
                copied.append(artifact)
                break
    return copied


def _build_solve_sh(oracle_files: list[str], workdir: str) -> str:
    if not oracle_files:
        body = 'echo "No oracle solution available for this task" >&2\nexit 1'
    else:
        body = "\n".join(f'cp "/solution/{f}" "{workdir}/{f}"' for f in oracle_files)
    return f"""#!/usr/bin/env bash
set -euo pipefail
{body}
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a skills-benchmarks task to Harbor format"
    )
    parser.add_argument("task", help="Task directory name under tasks/ (e.g. oss-fix-lc-streaming)")
    parser.add_argument("--out", default="harbor_tasks", help="Output root (default: harbor_tasks)")
    args = parser.parse_args()

    out = convert(args.task, REPO_ROOT / args.out)
    print(f"Wrote Harbor task: {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
