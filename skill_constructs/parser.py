"""Parser for skill.md files.

Reads skill.md files with XML-tagged sections and extracts content.
Used by __init__.py files to provide backwards-compatible section exports.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


def parse_skill_md(skill_md_path: Path) -> Dict[str, str]:
    """Parse skill.md and return sections dict keyed by tag name.

    Args:
        skill_md_path: Path to skill.md file

    Returns:
        Dict mapping tag names to their content (without the tags themselves)

    Example:
        {"frontmatter": "---\\nname: ...\\n---", "oneliner": "Build production-ready..."}
    """
    content = skill_md_path.read_text()
    sections = {}

    # Find all XML tags and their content
    # Pattern matches <tagname>content</tagname> including nested content
    pattern = r'<(\w+)>(.*?)</\1>'
    for match in re.finditer(pattern, content, re.DOTALL):
        tag_name = match.group(1)
        tag_content = match.group(2).strip()
        sections[tag_name] = tag_content

    return sections


def parse_skill_md_ordered(skill_md_path: Path) -> List[Tuple[str, str]]:
    """Parse skill.md and return sections as ordered list of (tag, content) tuples.

    Preserves the order of sections as they appear in the file.

    Args:
        skill_md_path: Path to skill.md file

    Returns:
        List of (tag_name, content) tuples in document order
    """
    content = skill_md_path.read_text()
    sections = []

    pattern = r'<(\w+)>(.*?)</\1>'
    for match in re.finditer(pattern, content, re.DOTALL):
        tag_name = match.group(1)
        tag_content = match.group(2).strip()
        sections.append((tag_name, tag_content))

    return sections


def load_skill_content(skill_md_path: Path) -> str:
    """Load full skill content from skill.md.

    Returns the raw file content. Useful for getting the complete skill
    as a single string.

    Args:
        skill_md_path: Path to skill.md file

    Returns:
        Full file content as string
    """
    return skill_md_path.read_text()


def get_section_list(skill_md_path: Path, exclude_tags: List[str] = None) -> List[str]:
    """Get ordered list of section contents (without tags).

    This is useful for building FULL_SECTIONS-style lists where you want
    all section contents joined together.

    Args:
        skill_md_path: Path to skill.md file
        exclude_tags: Optional list of tag names to exclude (e.g., ['frontmatter'])

    Returns:
        List of section content strings in document order
    """
    exclude_tags = exclude_tags or []
    sections = parse_skill_md_ordered(skill_md_path)
    return [content for tag, content in sections if tag not in exclude_tags]


def format_section_with_tags(tag: str, content: str) -> str:
    """Format content with XML tags for output.

    Useful when you need to reconstruct skill.md format.

    Args:
        tag: XML tag name
        content: Section content

    Returns:
        Formatted string with opening and closing tags
    """
    return f"<{tag}>\n{content}\n</{tag}>"


def load_skill(skill_dir: Path) -> dict:
    """Load skill from a skill directory containing skill.md.

    Provides a convenient interface for tests to load and select sections.

    Args:
        skill_dir: Path to skill directory (contains skill.md and optionally scripts/)

    Returns:
        Dict with:
        - sections: dict mapping tag names to content
        - all: list of all section contents in document order
        - scripts_dir: Path to scripts/ subdirectory (or None if doesn't exist)

    Example:
        trace = load_skill(Path("skill_constructs/langchain/langsmith_trace"))

        # Get specific sections
        my_sections = [
            trace["sections"]["frontmatter"],
            trace["sections"]["oneliner"],
            trace["sections"]["setup"],
        ]

        # Or get all sections
        full_sections = trace["all"]

        # Build skill config for treatment
        skill_config = {"sections": my_sections, "scripts_dir": trace["scripts_dir"]}
    """
    skill_md_path = skill_dir / "skill.md"
    sections = parse_skill_md(skill_md_path)
    all_sections = get_section_list(skill_md_path)
    scripts_dir = skill_dir / "scripts"

    return {
        "sections": sections,
        "all": all_sections,
        "scripts_dir": scripts_dir if scripts_dir.exists() else None,
    }


def split_skill(skill: dict, splits: Dict[str, List[str]], base_name: str = None) -> Dict[str, dict]:
    """Split one skill into multiple skill configs by section groups.

    Useful for experiments testing whether smaller, focused skills improve
    Claude's performance vs one large skill.

    Args:
        skill: Result from load_skill()
        splits: Dict mapping new skill names to lists of section tags to include
        base_name: Optional base name for frontmatter rewrite (e.g., "langsmith-trace")

    Returns:
        Dict mapping skill names to skill configs (sections list + scripts_dir)

    Example:
        trace = load_skill(Path("skill_constructs/langchain/langsmith_trace"))

        # Split into setup + querying skills
        split_skills = split_skill(trace, {
            "langsmith-trace-setup": ["frontmatter", "oneliner", "setup", "trace_langchain_oss"],
            "langsmith-trace-query": ["frontmatter", "oneliner", "command_structure", "querying_traces", "filters"],
        }, base_name="langsmith-trace")

        # Use in treatment
        treatment = Treatment(
            skills=split_skills,
            ...
        )
    """
    result = {}
    for skill_name, tags in splits.items():
        sections = []
        for tag in tags:
            content = skill.get("sections", {}).get(tag, "")
            if content:
                # Optionally rewrite frontmatter name for the split skill
                if tag == "frontmatter" and base_name and skill_name != base_name:
                    content = content.replace(f"name: {base_name}", f"name: {skill_name}")
                sections.append(content)
        result[skill_name] = {
            "sections": sections,
            "scripts_dir": skill.get("scripts_dir"),
        }
    return result


def skill_config(sections: List[str], scripts_dir: Path = None) -> dict:
    """Create a skill config dict for use in treatments.

    Convenience function for creating skill configs inline.

    Args:
        sections: List of section content strings
        scripts_dir: Optional path to scripts directory

    Returns:
        Dict with "sections" and "scripts_dir" keys

    Example:
        treatment = Treatment(
            skills={
                "my-skill": skill_config([HEADER, SETUP, EXAMPLES], scripts_dir),
            },
            ...
        )
    """
    return {"sections": sections, "scripts_dir": scripts_dir}
