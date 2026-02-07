"""Skill construction utilities."""

from pathlib import Path
from typing import List


def build_skill(sections: List[str]) -> str:
    """Assemble skill from list of section strings."""
    return "\n\n".join(s for s in sections if s and s.strip())


def write_skill(test_dir: Path, skill_name: str, content: str) -> Path:
    """Write skill content to .claude/skills/ directory."""
    skill_dir = test_dir / ".claude" / "skills" / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content)
    return skill_file


def setup_test_context(
    test_dir: Path,
    sections: List[str],
    claude_md: str = None,
    skill_name: str = "langchain-agents",
) -> None:
    """Setup test directory with .claude/ containing skills and CLAUDE.md.

    Args:
        test_dir: Test working directory
        sections: List of section strings to assemble into skill
        claude_md: Content for CLAUDE.md (None = no CLAUDE.md)
        skill_name: Name for the skill directory
    """
    claude_dir = test_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)

    if claude_md:
        (claude_dir / "CLAUDE.md").write_text(claude_md)

    content = build_skill(sections)
    write_skill(test_dir, skill_name, content)
