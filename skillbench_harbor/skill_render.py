"""Render a decomposed skill (skill.yaml + sections/*.md) into a single SKILL.md.

A skill is a directory containing:
  skill.yaml          frontmatter (name, description, optional language_names) + ordered `sections`
  sections/<id>.md            shared section body (plain markdown, no XML tags)
  sections/<id>.<lang>.md     OPTIONAL language variant (e.g. trace_example.py.md)

Rendering is a naive concatenation of the listed section bodies under a YAML
frontmatter block. For a language render, each section resolves to its
`<id>.<lang>.md` variant when present, else falls back to the shared `<id>.md`.
This keeps shared prose single-sourced so py/ts skills cannot drift apart.

CLI:
    uv run python -m skillbench_harbor.skill_render <skill_dir> --language py
"""

import argparse
import re
from pathlib import Path

import yaml

_SAFE_SECTION_ID = re.compile(r"^[A-Za-z0-9_-]+$")
_REQUIRED_KEYS = ("name", "description", "sections")


def load_skill(skill_dir: Path) -> dict:
    """Load and minimally validate a skill.yaml mapping."""
    meta = yaml.safe_load((Path(skill_dir) / "skill.yaml").read_text())
    if not isinstance(meta, dict):
        raise ValueError(f"{skill_dir}/skill.yaml must be a mapping")
    missing = [k for k in _REQUIRED_KEYS if k not in meta]
    if missing:
        raise ValueError(f"{skill_dir}/skill.yaml missing required keys: {missing}")
    if not isinstance(meta["sections"], list) or not meta["sections"]:
        raise ValueError(f"{skill_dir}/skill.yaml 'sections' must be a non-empty list")
    return meta


def _section_file(skill_dir: Path, section_id: str, language: str | None) -> Path | None:
    """Resolve a section to a file, or None if it doesn't apply to this language.

    Resolution: language variant -> shared file. If neither exists but the section
    has variants for *other* languages, it's a language-specific section that simply
    doesn't apply to this render, so return None (skip). Only a section id that
    matches no file at all is an error (typo guard).
    """
    if not _SAFE_SECTION_ID.match(section_id):
        raise ValueError(f"Unsafe section id: {section_id!r}")
    sections = Path(skill_dir) / "sections"
    if language:
        variant = sections / f"{section_id}.{language}.md"
        if variant.is_file():
            return variant
    base = sections / f"{section_id}.md"
    if base.is_file():
        return base
    if any(sections.glob(f"{section_id}.*.md")):
        return None  # language-specific section, not applicable to this language
    raise FileNotFoundError(
        f"No section file for {section_id!r} (language={language}) in {sections}"
    )


def skill_name(meta: dict, language: str | None) -> str:
    """Resolve a skill's display name, honoring a per-language override."""
    overrides = meta.get("language_names") or {}
    if language and language in overrides:
        return overrides[language]
    return meta["name"]


def _frontmatter(meta: dict, language: str | None) -> str:
    name = skill_name(meta, language)
    block = yaml.safe_dump(
        {"name": name, "description": meta["description"]},
        sort_keys=False,
        allow_unicode=True,
        width=10**9,  # keep the description on a single line
    ).strip()
    return f"---\n{block}\n---"


def render(skill_dir: Path, language: str | None = None) -> str:
    """Render the skill's SKILL.md text for the given language ('py', 'ts', or None)."""
    skill_dir = Path(skill_dir)
    meta = load_skill(skill_dir)
    parts = [_frontmatter(meta, language)]
    for section_id in meta["sections"]:
        path = _section_file(skill_dir, section_id, language)
        if path is not None:
            parts.append(path.read_text().strip())
    return "\n\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path, help="Path to the skill source directory.")
    parser.add_argument("--language", "-l", default=None, help="Language variant: py | ts.")
    args = parser.parse_args()
    print(render(args.skill_dir, args.language), end="")


if __name__ == "__main__":
    main()
