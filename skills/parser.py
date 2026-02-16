"""Parser for skill.md files.

Reads skill.md files with XML-tagged sections and extracts content.
Used by __init__.py files to provide backwards-compatible section exports.
"""

import re
from pathlib import Path


def parse_skill_md(skill_md_path: Path, keep_tags: bool = True) -> dict[str, str]:
    """Parse skill.md and return sections dict keyed by tag name.

    Frontmatter is extracted using --- delimiters (no XML tag needed).
    All other sections preserve their XML tags for delineation.

    Args:
        skill_md_path: Path to skill.md file
        keep_tags: If True, preserve XML tags around content (except frontmatter).

    Returns:
        Dict mapping tag names to their content

    Example:
        {"frontmatter": "---\\nname: ...\\n---", "oneliner": "<oneliner>\\nBuild...\\n</oneliner>"}
    """
    content = skill_md_path.read_text()
    sections = {}

    # Extract frontmatter using --- delimiters
    frontmatter_pattern = r"^---\n(.*?)\n---"
    fm_match = re.search(frontmatter_pattern, content, re.DOTALL)
    if fm_match:
        sections["frontmatter"] = f"---\n{fm_match.group(1).strip()}\n---"

    # Find all XML tags and their content (skip frontmatter if present)
    pattern = r"<(\w+)>(.*?)</\1>"
    for match in re.finditer(pattern, content, re.DOTALL):
        tag_name = match.group(1)
        if tag_name == "frontmatter":
            continue  # Already handled above
        tag_content = match.group(2).strip()

        if keep_tags:
            sections[tag_name] = f"<{tag_name}>\n{tag_content}\n</{tag_name}>"
        else:
            sections[tag_name] = tag_content

    return sections


def parse_skill_md_ordered(skill_md_path: Path, keep_tags: bool = True) -> list[tuple[str, str]]:
    """Parse skill.md and return sections as ordered list of (tag, content) tuples.

    Preserves the order of sections as they appear in the file.
    Frontmatter is extracted using --- delimiters and placed first.

    Args:
        skill_md_path: Path to skill.md file
        keep_tags: If True, preserve XML tags around content (except frontmatter).

    Returns:
        List of (tag_name, content) tuples in document order
    """
    content = skill_md_path.read_text()
    sections = []

    # Extract frontmatter using --- delimiters (always first)
    frontmatter_pattern = r"^---\n(.*?)\n---"
    fm_match = re.search(frontmatter_pattern, content, re.DOTALL)
    if fm_match:
        sections.append(("frontmatter", f"---\n{fm_match.group(1).strip()}\n---"))

    # Find all XML tags and their content (skip frontmatter if present)
    pattern = r"<(\w+)>(.*?)</\1>"
    for match in re.finditer(pattern, content, re.DOTALL):
        tag_name = match.group(1)
        if tag_name == "frontmatter":
            continue  # Already handled above
        tag_content = match.group(2).strip()

        if keep_tags:
            sections.append((tag_name, f"<{tag_name}>\n{tag_content}\n</{tag_name}>"))
        else:
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


def get_section_list(
    skill_md_path: Path, exclude_tags: list[str] = None, keep_tags: bool = True
) -> list[str]:
    """Get ordered list of section contents.

    This is useful for building FULL_SECTIONS-style lists where you want
    all section contents joined together.

    Args:
        skill_md_path: Path to skill.md file
        exclude_tags: Optional list of tag names to exclude (e.g., ['frontmatter'])
        keep_tags: If True, preserve XML tags around content (except frontmatter).

    Returns:
        List of section content strings in document order
    """
    exclude_tags = exclude_tags or []
    sections = parse_skill_md_ordered(skill_md_path, keep_tags=keep_tags)
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


# Script extension mapping for variant-based filtering
SCRIPT_EXTENSIONS = {
    "py": [".py"],
    "ts": [".ts", ".js", ".mjs", ".mts"],
    "all": None,  # No filtering - copy all scripts
}


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
        trace = load_skill(Path("skills/benchmarks/langsmith_trace"))

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


def load_skill_variant(skill_dir: Path, variant: str = None) -> dict:
    """Load skill from a specific .md file variant.

    Supports loading language-specific skill files (skill_py.md, skill_ts.md)
    or combined files (skill_all.md). The variant also determines which scripts
    get copied during test setup.

    Args:
        skill_dir: Path to skill directory
        variant: Variant name ("py", "ts", "all") or None for default skill.md

    Returns:
        Dict with:
        - sections: dict mapping tag names to content
        - all: list of all section contents in document order
        - scripts_dir: Path to scripts/ subdirectory (or None if doesn't exist)
        - script_filter: variant name (used to filter scripts during setup)

    Example:
        # Load Python variant - will filter to .py scripts during setup
        trace_py = load_skill_variant(Path("skills/benchmarks/langsmith_trace"), "py")

        # Load TypeScript variant - will filter to .ts/.js scripts during setup
        trace_ts = load_skill_variant(Path("skills/benchmarks/langsmith_trace"), "ts")

        # Load combined variant - will copy all scripts during setup
        trace_all = load_skill_variant(Path("skills/benchmarks/langsmith_trace"), "all")
    """
    if variant:
        skill_md_path = skill_dir / f"skill_{variant}.md"
    else:
        skill_md_path = skill_dir / "skill.md"

    if not skill_md_path.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_md_path}")

    sections = parse_skill_md(skill_md_path)
    all_sections = get_section_list(skill_md_path)
    scripts_dir = skill_dir / "scripts"

    return {
        "sections": sections,
        "all": all_sections,
        "scripts_dir": scripts_dir if scripts_dir.exists() else None,
        "script_filter": variant,
    }


def split_skill(
    skill: dict, splits: dict[str, list[str]], base_name: str = None
) -> dict[str, dict]:
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
        trace = load_skill(Path("skills/benchmarks/langsmith_trace"))

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


def skill_config(sections: list[str], scripts_dir: Path = None, script_filter: str = None) -> dict:
    """Create a skill config dict for use in treatments.

    Convenience function for creating skill configs inline.

    Args:
        sections: List of section content strings
        scripts_dir: Optional path to scripts directory
        script_filter: Optional filter for scripts ("py", "ts", "all")

    Returns:
        Dict with "sections", "scripts_dir", and "script_filter" keys

    Example:
        treatment = Treatment(
            skills={
                "my-skill": skill_config([HEADER, SETUP, EXAMPLES], scripts_dir, "py"),
            },
            ...
        )
    """
    return {"sections": sections, "scripts_dir": scripts_dir, "script_filter": script_filter}
