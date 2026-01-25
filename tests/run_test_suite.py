#!/usr/bin/env python3
"""Run Claude Code skill benchmarks.

Usage:
    .venv/bin/python tests/run_test_suite.py
    .venv/bin/python tests/run_test_suite.py --model haiku
    .venv/bin/python tests/run_test_suite.py -e SKILL_NEG SKILL_POS
    .venv/bin/python tests/run_test_suite.py -e framing -r 3
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent


def main():
    # Pass all args through to the test script
    cmd = [".venv/bin/python", "tests/basic_skill/test_langchain_context.py"] + sys.argv[1:]
    return subprocess.run(cmd, cwd=str(project_root)).returncode


if __name__ == "__main__":
    sys.exit(main())
