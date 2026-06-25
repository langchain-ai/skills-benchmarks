#!/usr/bin/env python3
"""Convert a skills-benchmarks task into a Harbor task directory.

Phase 0 of the Harbor migration. Targets the static `oss-*` tasks (single
bug-fix artifact, AST/regex validation). `lc-*` / `ls-*` tasks need extra
handling (data fixtures, LangSmith datasets) and are out of scope here.

Usage:
    uv run python scripts/convert_task.py oss-fix-lc-streaming
    uv run python scripts/convert_task.py oss-fix-lc-streaming --out harbor_tasks

What it emits (Harbor schema_version 1.3):
    <out>/<task>/task.toml
    <out>/<task>/instruction.md          # copied verbatim
    <out>/<task>/environment/            # Dockerfile (+ seed COPY) + workspace seed files
    <out>/<task>/tests/test.sh           # runs ported checks, writes /logs/verifier/reward.txt
    <out>/<task>/tests/<test_*.py>       # ported validation scripts (unchanged)
    <out>/<task>/tests/scaffold/...      # TestRunner + core helpers (unchanged)
    <out>/<task>/tests/_test_context.json
    <out>/<task>/solution/solve.sh       # oracle: drop the known-good artifact in place
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


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _copy_scaffold(tests_dir: Path) -> None:
    """Copy the TestRunner + core helpers so ported checks import unchanged."""
    dest = tests_dir / "scaffold" / "python" / "validation"
    dest.mkdir(parents=True, exist_ok=True)
    for level in (tests_dir / "scaffold", tests_dir / "scaffold" / "python", dest):
        (level / "__init__.py").write_text("")
    for name in ("runner.py", "core.py"):
        shutil.copy(SCAFFOLD_VALIDATION / name, dest / name)


def _build_task_toml(name: str, cfg: dict, workdir: str, verifier_user: str) -> str:
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
        "",
        "[environment]",
        "build_timeout_sec = 600.0",
        f"workdir = {_toml_str(workdir)}",
        "# skills_dir = \"skills\"  # Phase 1: per-treatment skills copied to the agent skills config dir",
        "",
    ]
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

    dockerfile = (src / "environment" / "Dockerfile").read_text()
    workdir = _detect_workdir(dockerfile)
    image_user = _detect_user(dockerfile)
    # The verifier writes to the Harbor-mounted /logs/verifier; run it as root
    # so it can write there regardless of the image's default USER.
    verifier_user = "root"

    out = out_root / task_name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # task.toml + instruction
    _write(out / "task.toml", _build_task_toml(task_name, cfg, workdir, verifier_user))
    shutil.copy(src / "instruction.md", out / "instruction.md")

    # environment: copy all build-context files, then append COPY for seed artifacts
    env_out = out / "environment"
    env_out.mkdir()
    for f in (src / "environment").iterdir():
        if f.is_file():
            shutil.copy(f, env_out / f.name)
    seed_copies = []
    chown = f"--chown={image_user}:{image_user} " if image_user else ""
    for artifact in target_artifacts:
        if (env_out / artifact).exists():
            seed_copies.append(f"COPY {chown}{artifact} {workdir}/{artifact}")
    if seed_copies:
        extra = "\n# [skillbench-harbor] seed the agent workspace with starting files\n"
        extra += "\n".join(seed_copies) + "\n"
        (env_out / "Dockerfile").write_text(dockerfile.rstrip() + "\n" + extra)

    # tests: ported scripts + scaffold + context + test.sh
    tests_out = out / "tests"
    tests_out.mkdir()
    for script in test_scripts:
        shutil.copy(src / "validation" / script, tests_out / script)
    _copy_scaffold(tests_out)
    _write(
        tests_out / "_test_context.json",
        json.dumps({"target_artifacts": target_artifacts}, indent=2),
    )
    _write(tests_out / "test.sh", _build_test_sh(test_scripts, workdir))

    # solution: oracle drops the known-good artifact(s) into the workspace
    sol_out = out / "solution"
    sol_out.mkdir()
    oracle_files = _collect_oracle(src, target_artifacts, sol_out)
    _write(sol_out / "solve.sh", _build_solve_sh(oracle_files, workdir))

    return out


def _build_test_sh(test_scripts: list[str], workdir: str) -> str:
    runs = "\n".join(
        f'python /tests/{s}\nstatus=$((status | $?))' for s in test_scripts
    )
    return f"""#!/usr/bin/env bash
# Run the ported validation checks and translate the result into a Harbor reward.
set -uo pipefail

export BENCH_TEST_CONTEXT="/tests/_test_context.json"
export BENCH_TEST_RESULTS="/logs/verifier/_test_results.json"
mkdir -p /logs/verifier

cd "{workdir}" || exit 1
export PYTHONPATH="/tests:${{PYTHONPATH:-}}"

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
    parser = argparse.ArgumentParser(description="Convert a skills-benchmarks task to Harbor format")
    parser.add_argument("task", help="Task directory name under tasks/ (e.g. oss-fix-lc-streaming)")
    parser.add_argument("--out", default="harbor_tasks", help="Output root (default: harbor_tasks)")
    args = parser.parse_args()

    out = convert(args.task, REPO_ROOT / args.out)
    print(f"Wrote Harbor task: {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
