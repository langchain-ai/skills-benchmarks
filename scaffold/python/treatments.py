"""Treatment loader for benchmark experiments.

Treatments are loaded from YAML configuration and built into Treatment objects
with fully-resolved skill configurations.

## Treatment Organization

Treatments are organized in the `treatments/` folder by category:
- `common/` - Shared treatments (CONTROL, ALL_MAIN_SKILLS, etc.)
- `langsmith/` - LS_* treatments for LangSmith tasks
- `langchain_concise/` - LCC_* treatments for LangChain tasks
- `oss_split/` - OSSS_* treatments for OSS fix tasks (granular skills)
- `oss_merged/` - OSSM_* treatments for OSS fix tasks (consolidated skills)

All treatments are shared across tasks - there are no task-specific treatments.

## Skill Configuration Options

Each skill in a treatment can be configured with:

1. **Basic loading**:
   - `skill`: Skill directory name (e.g., "langsmith_trace")
   - `name`: Custom skill name (defaults to skill dir with underscores replaced by dashes)
   - `variant`: Language variant to load ("py", "ts", "all", or None for skill.md)
   - `suffix`: Add "(Python)" or "(TypeScript)" to frontmatter description

2. **Section manipulation**:
   - `included_sections`: List of section names to include (filters to only these sections)
   - `section_overrides`: Dict of section name → custom content (replaces section content)
     Content can use any XML tags - not limited to original section's tags
   - `extra_sections`: List of content strings to append after all sections

   These can be combined:
   - `included_sections` alone: Filter to specified sections
   - `section_overrides` alone: Keep all sections, replace specified ones
   - `included_sections` + `section_overrides`: Filter AND replace
   - `extra_sections`: Always appended at the end

3. **Special modes**:
   - `noise`: Load from noise skill directory (skills/noise/)
   - `content`: Inline skill content (bypasses file loading entirely)
   - `include_related`: Include <related_skills> sections (filtered out by default)
   - `base`: Base directory for skills ("benchmarks" or "main", default: "benchmarks")

## YAML Anchor Pattern

Use YAML anchors for reusable content:

```yaml
_custom_section: &custom_section |
  <my_section>
  Custom content here
  </my_section>

TREATMENT_A:
  skills:
    - skill: my_skill
      included_sections: [frontmatter, oneliner]
      extra_sections:
        - *custom_section
```

Usage:
    from scaffold.python.treatments import load_treatments, load_treatment

    treatments = load_treatments()  # Load all shared treatments
    treatment = load_treatment("CONTROL")
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from scaffold.python.skill_parser import load_skill_variant, skill_config

TREATMENTS_FOLDER = Path(__file__).parent.parent.parent / "treatments"
SKILL_BASE = Path(__file__).parent.parent.parent / "skills" / "benchmarks"
MAIN_SKILL_BASE = Path(__file__).parent.parent.parent / "skills" / "main"
NOISE_SKILL_BASE = Path(__file__).parent.parent.parent / "skills" / "noise"

# All treatment categories (all shared, no task-specific folders)
TREATMENT_CATEGORIES = {
    "common",
    "langsmith",
    "langchain_concise",
    "oss_split",
    "oss_merged",
}


@dataclass
class TreatmentConfig:
    """Configuration for a treatment loaded from YAML."""

    name: str
    description: str
    claude_md: str = ""
    skills: list[dict[str, Any]] = field(default_factory=list)
    noise_tasks: list[str] = field(default_factory=list)


def _add_language_suffix(content: str, lang: str) -> str:
    """Add language suffix to frontmatter description."""
    suffix = "(Python)" if lang == "py" else "(TypeScript)"
    return re.sub(
        r'^(description: "?)(.+?)("?)$',
        rf"\1\2 {suffix}\3",
        content,
        count=1,
        flags=re.MULTILINE,
    )


def _filter_related_skills(sections: list[str]) -> list[str]:
    """Filter out related_skills sections."""
    return [s for s in sections if s and "<related_skills>" not in s]


def _build_skill_config(
    skill_dir: str,
    variant: str = "all",
    suffix: bool = False,
    include_related: bool = False,
    noise: bool = False,
    base: str = "benchmarks",
    included_sections: list[str] | None = None,
    extra_sections: list[str] | None = None,
    section_overrides: dict[str, str] | None = None,
) -> dict:
    """Build a skill configuration from a skill directory.

    Args:
        skill_dir: Skill directory name (e.g., "langsmith_trace" or "langsmith-trace")
        variant: Language variant to load (py, ts, all)
        suffix: Whether to add language suffix to description
        include_related: Whether to include <related_skills> sections from skill
        noise: Whether this is a noise/distractor skill (simpler loading)
        base: Base directory for skills ("benchmarks" or "main")
        included_sections: If specified, only include these named sections
        extra_sections: If specified, append these custom sections as content strings
        section_overrides: If specified, replace these sections with custom content

    Returns:
        Skill configuration dict for scaffold
    """
    if base == "main":
        skill_path = MAIN_SKILL_BASE / skill_dir
    else:
        skill_path = SKILL_BASE / skill_dir

    if noise:
        # Noise skills are in a separate directory with uppercase SKILL.md
        noise_path = NOISE_SKILL_BASE / skill_dir
        # Try SKILL.md (uppercase) first, then skill.md (lowercase)
        for filename in ["SKILL.md", "skill.md"]:
            skill_md = noise_path / filename
            if skill_md.exists():
                return skill_config([skill_md.read_text()], None, None)
        return None

    # Load skill - check if variant files exist, otherwise fall back to skill.md or SKILL.md
    variant_path = skill_path / f"skill_{variant}.md" if variant else skill_path / "skill.md"
    if variant and not variant_path.exists():
        # No variant files - try SKILL.md (uppercase) for main skills, then skill.md
        skill_md = None
        for filename in ["SKILL.md", "skill.md"]:
            if (skill_path / filename).exists():
                skill_md = skill_path / filename
                break

        if skill_md is None:
            raise FileNotFoundError(f"No skill file found in {skill_path}")

        # Parse directly since load_skill expects lowercase skill.md
        from scaffold.python.skill_parser import get_section_list, parse_skill_md

        sections = parse_skill_md(skill_md)
        all_sections = get_section_list(skill_md)
        scripts_dir = skill_path / "scripts"

        skill = {
            "sections": sections,
            "all": all_sections,
            "scripts_dir": scripts_dir if scripts_dir.exists() else None,
            "script_filter": None,  # No variant filtering
        }
    else:
        skill = load_skill_variant(skill_path, variant)

    # Select sections: either specific sections or all
    if included_sections:
        # Use only specified sections, with optional overrides
        sections = []
        for section_name in included_sections:
            if section_overrides and section_name in section_overrides:
                # Use override content instead of original
                sections.append(section_overrides[section_name])
            elif section_name in skill["sections"]:
                sections.append(skill["sections"][section_name])
    elif section_overrides:
        # Use all sections but apply overrides where specified
        sections = []
        for section_name, content in skill["sections"].items():
            if section_name in section_overrides:
                sections.append(section_overrides[section_name])
            else:
                sections.append(content)
    else:
        # Use all sections as-is
        sections = skill["all"]

    # Filter related_skills sections unless explicitly included
    if not include_related:
        sections = _filter_related_skills(sections)

    # Add custom extra sections if provided
    if extra_sections:
        sections = sections + extra_sections

    content = "\n\n".join(sections)

    # Add language suffix to description if requested
    if suffix and variant in ("py", "ts"):
        content = _add_language_suffix(content, variant)

    return skill_config([content], skill["scripts_dir"], skill["script_filter"])


def build_treatment_skills(skill_configs: list[dict[str, Any]]) -> dict[str, dict]:
    """Build skill dict from YAML skill configurations.

    Args:
        skill_configs: List of skill config dicts from YAML

    Returns:
        Dict mapping skill names to skill configurations
    """
    skills = {}

    for cfg in skill_configs:
        # Get or generate skill name
        name = cfg.get("name")
        skill_dir = cfg.get("skill")
        if not name and skill_dir:
            name = skill_dir.replace("_", "-")

        # Option 1: Inline content (for custom skill compositions)
        if "content" in cfg:
            skills[name] = skill_config([cfg["content"]], None, None)
            continue

        # Option 2: Load from skill directory
        variant = cfg.get("variant", "all")
        suffix = cfg.get("suffix", False)
        include_related = cfg.get("include_related", False)
        noise = cfg.get("noise", False)
        base = cfg.get("base", "benchmarks")  # "benchmarks" or "main"
        included_sections = cfg.get("included_sections")  # Optional list of section names
        extra_sections = cfg.get("extra_sections")  # Optional list of custom section content
        section_overrides = cfg.get("section_overrides")  # Optional dict of section replacements

        skill_cfg = _build_skill_config(
            skill_dir=skill_dir,
            variant=variant,
            suffix=suffix,
            include_related=include_related,
            noise=noise,
            base=base,
            included_sections=included_sections,
            extra_sections=extra_sections,
            section_overrides=section_overrides,
        )

        if skill_cfg:
            skills[name] = skill_cfg

    return skills


def load_treatments_yaml(path: Path) -> dict[str, TreatmentConfig]:
    """Load treatment configurations from a YAML file.

    Args:
        path: Path to treatments YAML file

    Returns:
        Dict mapping treatment names to TreatmentConfig objects
    """
    if not path.exists():
        raise FileNotFoundError(f"Treatments file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    treatments = {}
    for name, cfg in data.items():
        # Skip internal keys (anchors) starting with _
        if name.startswith("_"):
            continue
        treatments[name] = TreatmentConfig(
            name=name,
            description=cfg.get("description", ""),
            claude_md=cfg.get("claude_md", ""),
            skills=cfg.get("skills", []),
            noise_tasks=cfg.get("noise_tasks", []),
        )

    return treatments


def load_treatments() -> dict[str, TreatmentConfig]:
    """Load all treatments from the treatments/ folder structure.

    Returns:
        Dict mapping treatment names to TreatmentConfig objects
    """
    if not TREATMENTS_FOLDER.exists():
        return {}

    treatments = {}

    for category in TREATMENTS_FOLDER.iterdir():
        if not category.is_dir():
            continue
        if category.name not in TREATMENT_CATEGORIES:
            continue

        for yaml_file in category.glob("*.yaml"):
            category_treatments = load_treatments_yaml(yaml_file)
            treatments.update(category_treatments)

    return treatments


def load_treatment(name: str):
    """Load a single treatment by name and build it.

    Args:
        name: Treatment name

    Returns:
        Built Treatment object ready for use
    """
    from scaffold import Treatment

    configs = load_treatments()

    if name not in configs:
        raise KeyError(f"Treatment not found: {name}. Available: {list(configs.keys())}")

    cfg = configs[name]
    skills = build_treatment_skills(cfg.skills) if cfg.skills else {}

    return Treatment(
        description=cfg.description,
        skills=skills,
        claude_md=cfg.claude_md if cfg.claude_md else None,
        validators=[],  # Validators come from the task, not treatment
    )


def list_treatments() -> list[str]:
    """List available treatment names.

    Returns:
        List of treatment names
    """
    configs = load_treatments()
    return list(configs.keys())


# Legacy aliases for backward compatibility
def load_task_treatments(task_path: Path) -> dict[str, TreatmentConfig]:
    """Load treatments available for a task.

    Note: All treatments are now shared. This function returns all treatments
    regardless of task_path (kept for backward compatibility).

    Args:
        task_path: Path to task directory (ignored, kept for API compatibility)

    Returns:
        Dict mapping treatment names to TreatmentConfig objects
    """
    return load_treatments()


def get_task_treatment_names(task_path: Path) -> list[str]:
    """Get list of treatment names available for a task.

    Note: All treatments are now shared. This function returns all treatments
    regardless of task_path (kept for backward compatibility).

    Args:
        task_path: Path to task directory (ignored, kept for API compatibility)

    Returns:
        List of treatment names
    """
    return list_treatments()
