"""Skill constructs - modular sections for building test skills.

Structure:
  langchain/           - LangChain ecosystem skills
    langchain_agents/  - Build agents with modern patterns
    langsmith_trace/   - Query and analyze traces
    langsmith_dataset/ - Generate evaluation datasets
    langsmith_evaluator/ - Create custom evaluators
  pytest_fixtures/     - Test fixture patterns
"""

from pathlib import Path

# Load CLAUDE_SAMPLE.md content
_claude_sample_path = Path(__file__).parent / "CLAUDE_SAMPLE.md"
CLAUDE_SAMPLE = _claude_sample_path.read_text() if _claude_sample_path.exists() else ""

__all__ = ["CLAUDE_SAMPLE"]
