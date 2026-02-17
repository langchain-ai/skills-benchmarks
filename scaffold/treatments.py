"""Treatment loader for benchmark experiments.

Treatments are loaded from YAML configuration and built into Treatment objects
with fully-resolved skill configurations.

Usage:
    from scaffold.treatments import load_treatments, load_treatment

    treatments = load_treatments()  # Load all from tests/treatments.yaml
    treatment = load_treatment("SEPARATE_NAMES")
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from skills.parser import load_skill_variant, skill_config

TREATMENTS_FILE = Path(__file__).parent.parent / "tests" / "treatments.yaml"
SKILL_BASE = Path(__file__).parent.parent / "skills" / "benchmarks"


@dataclass
class TreatmentConfig:
    """Configuration for a treatment loaded from YAML."""

    name: str
    description: str
    claude_md: str = ""
    skills: list[dict[str, Any]] = field(default_factory=list)


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
) -> dict:
    """Build a skill configuration from a skill directory.

    Args:
        skill_dir: Skill directory name (e.g., "langsmith_trace")
        variant: Language variant to load (py, ts, all)
        suffix: Whether to add language suffix to description
        include_related: Whether to include <related_skills> sections
        noise: Whether this is a noise/distractor skill (simpler loading)

    Returns:
        Skill configuration dict for scaffold
    """
    skill_path = SKILL_BASE / skill_dir

    if noise:
        # Noise skills are simple - just load skill.md
        skill_md = skill_path / "skill.md"
        if skill_md.exists():
            return skill_config([skill_md.read_text()], None, None)
        return None

    # Load skill variant
    skill = load_skill_variant(skill_path, variant)
    sections = skill["all"]

    # Filter related_skills sections unless explicitly included
    if not include_related:
        sections = _filter_related_skills(sections)

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
        skill_dir = cfg.get("skill")
        name = cfg.get("name", skill_dir.replace("_", "-"))
        variant = cfg.get("variant", "all")
        suffix = cfg.get("suffix", False)
        include_related = cfg.get("include_related", False)
        noise = cfg.get("noise", False)

        skill_config = _build_skill_config(
            skill_dir=skill_dir,
            variant=variant,
            suffix=suffix,
            include_related=include_related,
            noise=noise,
        )

        if skill_config:
            skills[name] = skill_config

    return skills


def load_treatments_yaml(path: Path | None = None) -> dict[str, TreatmentConfig]:
    """Load treatment configurations from YAML file.

    Args:
        path: Optional path to treatments.yaml

    Returns:
        Dict mapping treatment names to TreatmentConfig objects
    """
    path = path or TREATMENTS_FILE

    if not path.exists():
        raise FileNotFoundError(f"Treatments file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    treatments = {}
    for name, cfg in data.items():
        treatments[name] = TreatmentConfig(
            name=name,
            description=cfg.get("description", ""),
            claude_md=cfg.get("claude_md", ""),
            skills=cfg.get("skills", []),
        )

    return treatments


def load_treatment(name: str, path: Path | None = None) -> "Treatment":
    """Load a single treatment by name and build it.

    Args:
        name: Treatment name
        path: Optional path to treatments.yaml

    Returns:
        Built Treatment object ready for use
    """
    from scaffold import Treatment

    configs = load_treatments_yaml(path)

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


def list_treatments(path: Path | None = None) -> list[str]:
    """List available treatment names.

    Args:
        path: Optional path to treatments.yaml

    Returns:
        List of treatment names
    """
    configs = load_treatments_yaml(path)
    return list(configs.keys())
