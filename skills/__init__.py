"""Skill constructs - modular sections for building test skills.

Structure:
  benchmarks/            - Skills used in benchmark tests
    langchain_basic/     - Build agents with modern patterns (skill: langchain-agents)
    langsmith_trace/     - Query and analyze traces
    langsmith_dataset/   - Generate evaluation datasets
    langsmith_evaluator/ - Create custom evaluators
  main/                  - Production-ready skills
  noise/                 - Distractor skills for noise tests
"""

from pathlib import Path

# Load sample CLAUDE.md content for tests
_claude_md_path = Path(__file__).parent / "CLAUDE.md"
CLAUDE_FULL = _claude_md_path.read_text() if _claude_md_path.exists() else ""

__all__ = ["CLAUDE_FULL"]
