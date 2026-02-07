#!/usr/bin/env python3
"""Generate SKILL_SAMPLE.md files from FULL_SECTIONS for all skills.

Run from repo root:
    python skill_constructs/construct.py

This generates the full skill documentation from the modular sections.
DEFAULT_SECTIONS are used in tests, FULL_SECTIONS for complete docs.
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))


def generate_skill_sample(skill_module_path: str, output_path: Path) -> None:
    """Generate SKILL_SAMPLE.md from FULL_SECTIONS.

    Args:
        skill_module_path: Import path like 'skill_constructs.langchain.langsmith_trace.skill'
        output_path: Path to write SKILL_SAMPLE.md
    """
    import importlib
    module = importlib.import_module(skill_module_path)
    sections = module.FULL_SECTIONS

    content = '\n\n'.join(sections)
    output_path.write_text(content)
    print(f"Generated {output_path} ({len(sections)} sections)")


def main():
    skills_dir = Path(__file__).parent / "langchain"

    skills = [
        ("skill_constructs.langchain.langsmith_trace.skill", skills_dir / "langsmith_trace" / "SKILL_SAMPLE.md"),
        ("skill_constructs.langchain.langsmith_dataset.skill", skills_dir / "langsmith_dataset" / "SKILL_SAMPLE.md"),
        ("skill_constructs.langchain.langsmith_evaluator.skill", skills_dir / "langsmith_evaluator" / "SKILL_SAMPLE.md"),
        ("skill_constructs.langchain.langchain_agents.skill", skills_dir / "langchain_agents" / "AGENTS.md"),
    ]

    for module_path, output_path in skills:
        generate_skill_sample(module_path, output_path)

    print("\nDone - all SKILL_SAMPLE.md files regenerated from FULL_SECTIONS")


if __name__ == "__main__":
    main()
