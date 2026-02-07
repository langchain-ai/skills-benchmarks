"""Test runner for Claude Code CLI."""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Callable
from dotenv import load_dotenv
from .capture import parse_output, extract_events, save_events

load_dotenv(Path(__file__).parent.parent / ".env")
PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class TestResult:
    name: str
    passed: bool
    checks_passed: List[str]
    checks_failed: List[str]
    events: Dict[str, Any]


@dataclass
class RepetitionResult:
    name: str
    runs: List[TestResult]
    pass_rate: float
    consistent: bool
    check_frequencies: Dict[str, int]


def run_claude(prompt: str, cwd: Path, timeout: int = 300, model: str = None) -> Dict[str, Any]:
    """Run Claude Code and return parsed events."""
    cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions",
           "--output-format", "stream-json", "--verbose"]
    if model:
        cmd.extend(["--model", model])
    result = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=str(cwd), env=os.environ.copy())
    return extract_events(parse_output(result.stdout))


def run_test(
    name: str, prompt: str, test_dir: Path,
    validate: Callable[[Dict, Path], tuple[List[str], List[str]]],
    timeout: int = 300, model: str = None, save: bool = True,
) -> TestResult:
    """Run a test and validate results."""
    print(f"[TEST] {name}")
    try:
        events = run_claude(prompt, test_dir, timeout, model)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after {timeout}s")
        return TestResult(name, False, [], ["Timeout"], {})

    if save:
        save_events(events, PROJECT_ROOT / "logs" / "events", name)

    passed, failed = validate(events, test_dir)
    ok = len(failed) == 0
    print(f"{'PASS' if ok else 'FAIL'}: {len(passed)} checks" +
          (f", {len(failed)} failed" if failed else ""))
    for f in failed:
        print(f"  {f}")

    return TestResult(name, ok, passed, failed, events)


def run_with_repetition(
    name: str, prompt: str, make_dir: Callable[[], Path],
    validate: Callable[[Dict, Path], tuple[List[str], List[str]]],
    repetitions: int = 3, timeout: int = 300, model: str = None,
) -> RepetitionResult:
    """Run a test multiple times to check consistency."""
    runs = []
    for i in range(repetitions):
        print(f"\n--- Run {i+1}/{repetitions} ---")
        runs.append(run_test(f"{name}_run{i+1}", prompt, make_dir(), validate, timeout, model))

    pass_count = sum(1 for r in runs if r.passed)
    pass_rate = pass_count / len(runs)
    consistent = len(set(r.passed for r in runs)) == 1

    check_freq = {}
    for r in runs:
        for check in r.checks_passed:
            check_freq[check] = check_freq.get(check, 0) + 1

    print(f"\n{'='*50}\nREPETITION SUMMARY: {name}\n{'='*50}")
    print(f"Pass rate: {pass_count}/{len(runs)} ({pass_rate*100:.0f}%)")
    print(f"Consistent: {'Yes' if consistent else 'No'}")
    if check_freq:
        print("Check frequencies:")
        for check, count in sorted(check_freq.items(), key=lambda x: -x[1]):
            print(f"  {check}: {count}/{len(runs)}")

    return RepetitionResult(name, runs, pass_rate, consistent, check_freq)
