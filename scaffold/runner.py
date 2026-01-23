"""Test runner for Claude Code CLI."""

import os
import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Callable
from enum import Enum

from dotenv import load_dotenv
from .capture import parse_output, extract_events, save_events, summarize

load_dotenv(Path(__file__).parent.parent / ".env")
PROJECT_ROOT = Path(__file__).parent.parent


class ContextMode(Enum):
    NONE = "none"
    CLAUDE_MD_ONLY = "claude_md_only"
    SKILLS_ONLY = "skills_only"
    FULL = "full"


@dataclass
class TestResult:
    name: str
    passed: bool
    checks_passed: List[str]
    checks_failed: List[str]
    events: Dict[str, Any]
    context: ContextMode = ContextMode.NONE


def setup_context(test_dir: Path, mode: ContextMode) -> None:
    """Copy context files to test directory."""
    if mode in (ContextMode.CLAUDE_MD_ONLY, ContextMode.FULL):
        src = PROJECT_ROOT / "CLAUDE.md"
        if src.exists():
            shutil.copy2(src, test_dir / "CLAUDE.md")
    if mode in (ContextMode.SKILLS_ONLY, ContextMode.FULL):
        src = PROJECT_ROOT / "skills"
        if src.exists():
            shutil.copytree(src, test_dir / "skills")


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
    name: str,
    prompt: str,
    test_dir: Path,
    validate: Callable[[Dict, Path], tuple[List[str], List[str]]],
    timeout: int = 300,
    model: str = None,
    context: ContextMode = None,
    save: bool = True,
) -> TestResult:
    """Run a test and validate results."""
    if context:
        setup_context(test_dir, context)

    print(f"[TEST] {name}")

    try:
        events = run_claude(prompt, test_dir, timeout, model)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after {timeout}s")
        return TestResult(name, False, [], ["Timeout"], {}, context or ContextMode.NONE)

    if save:
        save_events(events, PROJECT_ROOT / "logs" / "events", name)

    passed, failed = validate(events, test_dir)
    ok = len(failed) == 0
    print(f"{'PASS' if ok else 'FAIL'}: {len(passed)} checks" +
          (f", {len(failed)} failed" if failed else ""))
    for f in failed:
        print(f"  {f}")

    return TestResult(name, ok, passed, failed, events, context or ContextMode.NONE)


def run_comparison(
    name: str,
    prompt: str,
    make_dir: Callable[[], Path],
    validate: Callable[[Dict, Path], tuple[List[str], List[str]]],
    modes: List[ContextMode] = None,
    timeout: int = 300,
    model: str = None,
) -> Dict[ContextMode, TestResult]:
    """Run same test with different context modes."""
    modes = modes or [ContextMode.NONE, ContextMode.FULL]
    results = {}

    for mode in modes:
        print(f"\n{'='*50}\n{name} [{mode.value}]\n{'='*50}\n")
        results[mode] = run_test(f"{name} [{mode.value}]", prompt,
                                make_dir(), validate, timeout, model, mode)

    print(f"\n{'='*50}\nCOMPARISON: {name}\n{'='*50}")
    for mode, r in results.items():
        print(f"  [{mode.value:15}] {'PASS' if r.passed else 'FAIL'} - {len(r.checks_passed)} checks")
    return results
