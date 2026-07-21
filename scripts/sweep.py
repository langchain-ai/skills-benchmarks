#!/usr/bin/env python3
"""Sweep a Harbor task across treatments and aggregate the results.

Each treatment is materialized into a ``skills_dir`` (one ``<skill>/SKILL.md`` per
skill) and injected via Harbor's native ``--skills`` flag, so any skill-aware agent
(claude-code, codex, langgraph/deepagents, ...) works via ``--agent``. For each
(task x treatment x rep) cell we run scripts/harbor_run.sh, then collect the verifier
reward and per-check pass/fail breakdown into a comparison table and sweep-summary.json.

Usage:
    uv run python scripts/sweep.py \\
      --task harbor_tasks/oss-fix-lc-streaming \\
      --treatment CONTROL,ALL_MAIN_SKILLS \\
      -m anthropic/claude-sonnet-4-6

    # different agent, TS skill variants, repeatable --task, glob treatments, reps
    uv run python scripts/sweep.py --task a --task b --treatment 'MAIN_*' \\
      --agent codex --language ts --count 3
"""

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import tomllib
import uuid
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
HARBOR_RUN = REPO_DIR / "scripts" / "harbor_run.sh"
JOBS_DIR = REPO_DIR / "jobs"
SKILLS_STAGING = REPO_DIR / ".sweep" / "skills"
DEEPAGENTS_BASE = REPO_DIR / "deepagents_agent"
DEEPAGENTS_STAGING = REPO_DIR / ".sweep" / "deepagents"
LS_SETUP_DIR = REPO_DIR / ".sweep" / "ls-setup"

# Load .env so host-side LangSmith calls (ls_setup/ls_cleanup) pick up LANGSMITH_API_KEY.
_env_file = REPO_DIR / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            _k = _k.strip()
            if _k not in os.environ:
                os.environ[_k] = _v.strip().strip('"').strip("'")

sys.path.insert(0, str(REPO_DIR))
from skillbench_harbor.treatments import list_treatments, materialize_treatment  # noqa: E402


def expand_treatments(spec: str) -> list[str]:
    """Expand a comma-separated list of names / fnmatch globs to treatment names."""
    available = list_treatments()
    selected: list[str] = []
    for token in (t.strip() for t in spec.split(",") if t.strip()):
        if any(c in token for c in "*?[]"):
            matches = sorted(n for n in available if fnmatch.fnmatch(n, token))
            if not matches:
                raise SystemExit(f"No treatments match pattern: {token}")
            selected.extend(matches)
        else:
            if token not in available:
                raise SystemExit(f"Treatment not found: {token}. Available: {sorted(available)}")
            selected.append(token)
    return list(dict.fromkeys(selected))


def stage_treatment(treatment: str, language: str | None) -> Path | None:
    """Materialize a treatment's skills into a clean staging dir.

    Returns the dir, or None if the treatment has no skills (CONTROL) so the caller
    omits ``--skills`` entirely.
    """
    if "/" in treatment or "\\" in treatment or treatment in (".", ".."):
        raise SystemExit(f"Unsafe treatment name: {treatment!r}")
    suffix = f"-{language}" if language else ""
    dest = (SKILLS_STAGING / f"{treatment}{suffix}").resolve()
    if SKILLS_STAGING.resolve() not in dest.parents:
        raise SystemExit(f"Staging path escapes workspace: {treatment!r}")
    if dest.exists():
        shutil.rmtree(dest)
    materialize_treatment(treatment, dest, language=language)
    return dest if any(dest.iterdir()) else None


def stage_deepagents_project(treatment: str, skills_dir: Path | None) -> Path:
    """Copy deepagents_agent/ into a per-treatment staging dir, baking in skills."""
    if "/" in treatment or "\\" in treatment or treatment in (".", ".."):
        raise SystemExit(f"Unsafe treatment name: {treatment!r}")
    dest = (DEEPAGENTS_STAGING / treatment).resolve()
    if DEEPAGENTS_STAGING.resolve() not in dest.parents:
        raise SystemExit(f"Staging path escapes workspace: {treatment!r}")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(DEEPAGENTS_BASE, dest)
    if skills_dir is not None:
        shutil.copytree(skills_dir, dest / "skills", dirs_exist_ok=True)
    return dest


def _is_ls_task(task: str) -> tuple[bool, str, dict]:
    """Check if a harbor task originated from an ls-* source (has [template] in source task.toml).

    Returns (is_ls, source_task_name, source_cfg).
    """
    try:
        harbor_cfg = tomllib.loads((Path(task) / "task.toml").read_text())
        src_name = harbor_cfg.get("metadata", {}).get("source_task", "")
        if not src_name:
            return False, "", {}
        src_toml = REPO_DIR / "tasks" / src_name / "task.toml"
        if not src_toml.exists():
            return False, src_name, {}
        src_cfg = tomllib.loads(src_toml.read_text())
        return "template" in src_cfg, src_name, src_cfg
    except Exception:
        return False, "", {}


def ls_setup(task: str, src_name: str, src_cfg: dict) -> tuple[str, Path]:
    """Upload LangSmith data for an ls-* task and write a resolved extra instruction.

    Returns (run_id, extra_instruction_path).
    """
    sys.path.insert(0, str(REPO_DIR))
    from scaffold.python.external_data_handler import (  # noqa: PLC0415
        upload_datasets,
        upload_traces,
    )

    run_id = uuid.uuid4().hex[:8]
    project = f"bench-{run_id}"
    data_dir = REPO_DIR / "tasks" / src_name / "data"
    setup = src_cfg.get("setup", {})
    handlers = setup.get("data", [])
    if isinstance(handlers, dict):
        handlers = [handlers]

    for handler in handlers:
        handler_name = handler.get("handler", "")
        if handler_name == "upload_traces" and data_dir.exists():
            print(f"[ls-setup] Uploading traces → project: {project}")
            upload_traces(project=project, data_dir=data_dir)
        elif handler_name == "upload_datasets" and data_dir.exists():
            print(f"[ls-setup] Uploading datasets (run_id={run_id})")
            upload_datasets(data_dir=data_dir, run_id=run_id)

    # Resolve template vars: "bench-sql-{run_id}" → "bench-sql-<run_id>"
    template_vars = setup.get("template_vars", {})
    resolved: dict[str, str] = {"run_id": run_id}
    for k, v in template_vars.items():
        resolved[k] = v.replace("{run_id}", run_id)

    LS_SETUP_DIR.mkdir(parents=True, exist_ok=True)
    extra_path = LS_SETUP_DIR / f"{src_name}-{run_id}.md"
    lines = [
        "## Run Configuration",
        "",
        "The following values have been resolved for this benchmark run.",
        "Use these exact names when creating or uploading resources to LangSmith.",
        "",
        f"- **run_id**: `{run_id}`",
        f"- **LangSmith project for traces**: `{project}`",
    ]
    for k, v in resolved.items():
        if k != "run_id":
            lines.append(f"- **{k}**: `{v}`")
    lines += [
        "",
        "When the instructions reference `{run_id}`, `{py_dataset}`, etc.,",
        f"substitute the resolved values above (e.g., `{{run_id}}` → `{run_id}`).",
    ]
    extra_path.write_text("\n".join(lines))
    return run_id, extra_path


def ls_cleanup(run_id: str) -> None:
    """Delete all LangSmith resources namespaced to this run_id."""
    sys.path.insert(0, str(REPO_DIR))
    from scaffold.python.external_data_handler import cleanup_namespace  # noqa: PLC0415
    print(f"[ls-cleanup] Deleting namespace: {run_id}")
    cleanup_namespace(run_id)


def _snapshot_jobs() -> set[Path]:
    return set(JOBS_DIR.glob("*/")) if JOBS_DIR.exists() else set()


def _read_results(job_dir: Path) -> dict:
    """Read reward + passed/failed checks from a job's verifier output."""
    result = {"job_dir": str(job_dir.relative_to(REPO_DIR)), "reward": None,
              "passed": [], "failed": []}

    reward_files = list(job_dir.glob("*/verifier/reward.txt"))
    if reward_files:
        try:
            result["reward"] = float(reward_files[0].read_text().strip())
        except ValueError:
            pass

    test_results = list(job_dir.glob("*/verifier/_test_results.json"))
    if test_results:
        data = json.loads(test_results[0].read_text())
        result["passed"] = data.get("passed", [])
        result["failed"] = data.get("failed", [])

    return result


def run_cell(
    task: str, treatment: str, model: str, agent: str, skills_dir: Path | None,
    *, env: str = "docker", project_path: Path | None = None,
    extra_instruction_paths: list[Path] | None = None,
    verifier_run_id: str | None = None,
) -> dict:
    """Run one harbor trial and return its parsed results."""
    before = _snapshot_jobs()
    argv = [
        str(HARBOR_RUN),
        "--path", task,
        "--agent", agent,
        "-m", model,
        "--env", env,
    ]
    if project_path is not None:
        argv += ["--ak", f"project_path={project_path}", "--ak", "graph=coding_agent"]
    elif skills_dir is not None:
        argv += ["--skills", str(skills_dir)]
    for p in (extra_instruction_paths or []):
        argv += ["--extra-instruction-path", str(p)]
    if verifier_run_id:
        argv += ["--ve", f"RUN_ID={verifier_run_id}"]
    print(f"\n=== {task} | {treatment} | {agent} | {model} ===", flush=True)
    proc = subprocess.run(argv)  # inherit stdout/stderr so progress is visible

    new_jobs = _snapshot_jobs() - before
    if not new_jobs:
        return {"task": task, "treatment": treatment, "exit_code": proc.returncode,
                "reward": None, "passed": [], "failed": [], "job_dir": None}

    job_dir = max(new_jobs, key=lambda p: p.stat().st_mtime)
    record = {"task": task, "treatment": treatment, "exit_code": proc.returncode}
    record.update(_read_results(job_dir))
    return record


def print_table(records: list[dict]) -> None:
    """Print a compact comparison table grouped by task."""
    print("\n" + "=" * 72)
    print("SWEEP SUMMARY")
    print("=" * 72)
    for task in dict.fromkeys(r["task"] for r in records):
        print(f"\n{task}")
        print(f"  {'treatment':<22} {'reward':>7}  {'checks':>8}  failed")
        print(f"  {'-' * 22} {'-' * 7}  {'-' * 8}  {'-' * 20}")
        for r in (r for r in records if r["task"] == task):
            n_pass = len(r["passed"])
            total = n_pass + len(r["failed"])
            reward = "—" if r["reward"] is None else f"{r['reward']:.1f}"
            checks = f"{n_pass}/{total}" if total else "—"
            failed = ", ".join(f.split(":")[0] for f in r["failed"]) or "—"
            print(f"  {r['treatment']:<22} {reward:>7}  {checks:>8}  {failed}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", action="append", required=True,
                        help="Path to a harbor task dir (repeatable).")
    parser.add_argument("--treatment", default="CONTROL,ALL_MAIN_SKILLS",
                        help="Comma-separated treatment names / globs.")
    parser.add_argument("-m", "--model", default="claude-sonnet-4-6",
                        help="Model name passed to the agent. Bare id (no "
                             "provider prefix): under the LangSmith gateway "
                             "base URL the adapter forwards it verbatim.")
    parser.add_argument("-a", "--agent", default="claude-code",
                        help="Harbor agent name (claude-code, codex, langgraph, ...).")
    parser.add_argument("-e", "--env", default="docker",
                        help="Harbor environment type (docker, langsmith, ...).")
    parser.add_argument("-l", "--language", default=None, choices=["py", "ts"],
                        help="Render decomposed skills for this language variant.")
    parser.add_argument("--count", type=int, default=1, help="Repetitions per cell.")
    parser.add_argument("--out", default="sweep-summary.json",
                        help="Path to write the JSON summary.")
    parser.add_argument("--no-cleanup", action="store_true",
                        help="Skip LangSmith namespace cleanup after ls-* runs (useful for inspection).")
    args = parser.parse_args()

    treatments = expand_treatments(args.treatment)
    staged_skills = {t: stage_treatment(t, args.language) for t in treatments}
    staged_projects: dict[str, Path] = {}
    if args.agent == "langgraph":
        staged_projects = {t: stage_deepagents_project(t, staged_skills[t]) for t in treatments}

    records: list[dict] = []
    for task in args.task:
        is_ls, src_name, src_cfg = _is_ls_task(task)
        for treatment in treatments:
            for rep in range(args.count):
                run_id = ""
                extra_paths: list[Path] = []
                if is_ls:
                    run_id, extra_path = ls_setup(task, src_name, src_cfg)
                    extra_paths = [extra_path]
                try:
                    record = run_cell(
                        task, treatment, args.model, args.agent, staged_skills[treatment],
                        env=args.env,
                        project_path=staged_projects.get(treatment),
                        extra_instruction_paths=extra_paths or None,
                        verifier_run_id=run_id or None,
                    )
                finally:
                    if run_id and not args.no_cleanup:
                        ls_cleanup(run_id)
                    elif run_id:
                        print(f"[ls-cleanup] Skipped — namespace bench-{run_id} left in LangSmith")
                record["rep"] = rep
                records.append(record)

    print_table(records)
    out_path = Path(args.out)
    out_path.write_text(json.dumps(records, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
