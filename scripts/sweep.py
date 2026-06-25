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
import shutil
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
HARBOR_RUN = REPO_DIR / "scripts" / "harbor_run.sh"
JOBS_DIR = REPO_DIR / "jobs"
SKILLS_STAGING = REPO_DIR / ".sweep" / "skills"

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


def run_cell(task: str, treatment: str, model: str, agent: str, skills_dir: Path | None) -> dict:
    """Run one harbor trial and return its parsed results."""
    before = _snapshot_jobs()
    argv = [
        str(HARBOR_RUN),
        "--path", task,
        "--agent", agent,
        "-m", model,
    ]
    if skills_dir is not None:
        argv += ["--skills", str(skills_dir)]
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
    parser.add_argument("-m", "--model", default="anthropic/claude-sonnet-4-6",
                        help="Model name passed to the agent.")
    parser.add_argument("-a", "--agent", default="claude-code",
                        help="Harbor agent name (claude-code, codex, langgraph, ...).")
    parser.add_argument("-l", "--language", default=None, choices=["py", "ts"],
                        help="Render decomposed skills for this language variant.")
    parser.add_argument("--count", type=int, default=1, help="Repetitions per cell.")
    parser.add_argument("--out", default="sweep-summary.json",
                        help="Path to write the JSON summary.")
    args = parser.parse_args()

    treatments = expand_treatments(args.treatment)
    staged = {t: stage_treatment(t, args.language) for t in treatments}

    records: list[dict] = []
    for task in args.task:
        for treatment in treatments:
            for rep in range(args.count):
                record = run_cell(task, treatment, args.model, args.agent, staged[treatment])
                record["rep"] = rep
                records.append(record)

    print_table(records)
    out_path = Path(args.out)
    out_path.write_text(json.dumps(records, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
