"""Treatment loader + materializer for benchmark experiments (Harbor migration).

A treatment is a *named list of skill references* — compositional, not subtractive.
There is no section filtering: a skill is brought in whole, and a treatment simply
concatenates the skills it names.

    TREATMENT_NAME:
      description: "..."
      skills:
        - main/langchain-fundamentals     # whole-file skill (used as-is)
        - benchmarks/langsmith_trace      # decomposed skill (rendered on demand)
        - noise/api_docs                  # noise/distractor — just another entry

Each skill ref is a path relative to the skills root (``skills/``). Naming skills by
path disambiguates collisions across the main/benchmarks/noise trees. A ref may also
point directly at a single ``.md`` file. ``CONTROL`` (empty ``skills``) is a no-op.

Materializing a treatment writes one ``<skill-name>/SKILL.md`` folder per skill into a
destination directory — the agent-agnostic ``skills_dir`` layout Harbor injects via
``--skills`` for ANY coding agent (claude-code, codex, deepagents, ...).

Two bring-in modes, auto-detected per ref:
  - Decomposed: dir with ``skill.yaml`` + ``sections/`` -> rendered via skill_render,
    then bundled extras (e.g. ``references/``) copied alongside.
  - Whole-file: dir with ``SKILL.md`` (copied as-is, including bundled files), or a
    single ``.md`` file (copied to ``<name>/SKILL.md``).

Language ('py' | 'ts' | None) is a render-time axis applied to decomposed skills so
shared prose stays single-sourced; whole-file skills are language-agnostic and copied
unchanged.
"""

import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from skillbench_harbor.skill_render import load_skill, render, skill_name

# Files that are decomposition *sources*, not skill payload — excluded when copying
# a decomposed skill's bundled extras (its SKILL.md is rendered fresh instead).
_DECOMP_SOURCES = {"skill.yaml", "skill_all.md", "skill_py.md", "skill_ts.md"}
_DECOMP_DIRS = {"sections"}


def _repo_root() -> Path:
    """Resolve the skills-benchmarks repo root.

    Order: ``SKILLBENCH_REPO_ROOT`` env override, then walk up from this file
    looking for a directory that contains both ``treatments/`` and ``skills/``.
    The env override lets this work when the package is shipped away from the repo
    (e.g. LangSmith cloud sandboxes).
    """
    override = os.environ.get("SKILLBENCH_REPO_ROOT")
    if override:
        return Path(override).resolve()

    for candidate in Path(__file__).resolve().parents:
        if (candidate / "treatments").is_dir() and (candidate / "skills").is_dir():
            return candidate

    return Path(__file__).resolve().parent.parent


_ROOT = _repo_root()
TREATMENTS_FOLDER = _ROOT / "treatments"
SKILLS_ROOT = _ROOT / "skills"


@dataclass
class TreatmentConfig:
    """A treatment: a name, a description, and an ordered list of skill refs."""

    name: str
    description: str = ""
    skills: list[str] = field(default_factory=list)


def _coerce_skill_refs(raw) -> list[str] | None:
    """Return the skill refs if they are a clean list of strings, else None.

    A None result flags a legacy/invalid entry (e.g. the old list-of-dicts format)
    so the loader can skip it with a warning rather than crash.
    """
    if not isinstance(raw, list):
        return None
    if not all(isinstance(item, str) for item in raw):
        return None
    return raw


def load_treatments_yaml(path: Path) -> dict[str, TreatmentConfig]:
    """Load treatments from one YAML file (skips ``_``-prefixed anchor keys)."""
    data = yaml.safe_load(path.read_text()) or {}
    treatments: dict[str, TreatmentConfig] = {}
    for name, cfg in data.items():
        if name.startswith("_") or not isinstance(cfg, dict):
            continue
        refs = _coerce_skill_refs(cfg.get("skills", []))
        if refs is None:
            print(
                f"[treatments] skipping legacy/invalid treatment {name!r} in {path} "
                "(skills must be a list of string refs)",
                file=sys.stderr,
            )
            continue
        treatments[name] = TreatmentConfig(
            name=name,
            description=cfg.get("description", ""),
            skills=refs,
        )
    return treatments


def load_treatments() -> dict[str, TreatmentConfig]:
    """Load all treatments found under ``treatments/`` (recursively).

    Directories whose name starts with ``_`` (e.g. ``_archive/``) are skipped, so
    retired treatments can be parked there without being loaded or warned about.
    """
    if not TREATMENTS_FOLDER.exists():
        return {}
    treatments: dict[str, TreatmentConfig] = {}
    for yaml_file in sorted(TREATMENTS_FOLDER.rglob("*.yaml")):
        rel = yaml_file.relative_to(TREATMENTS_FOLDER)
        if any(part.startswith("_") for part in rel.parts):
            continue
        treatments.update(load_treatments_yaml(yaml_file))
    return treatments


def list_treatments() -> list[str]:
    """List available treatment names."""
    return list(load_treatments().keys())


def _resolve_skill_ref(ref: str) -> Path:
    """Resolve a skill ref against the skills root, guarding against traversal."""
    root = SKILLS_ROOT.resolve()
    target = (SKILLS_ROOT / ref).resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"Skill ref escapes skills root: {ref!r}")
    if not target.exists():
        raise FileNotFoundError(f"Skill ref not found: {ref!r} (looked in {SKILLS_ROOT})")
    return target


def _safe_skill_dirname(name: str, dest_dir: Path) -> Path:
    """Resolve ``dest_dir/<name>`` and guard against path traversal.

    The destination folder name comes from a skill's frontmatter, so a stray ``/``
    or ``..`` must never let a materialized directory escape ``dest_dir``.
    """
    if not name or name in (".", ".."):
        raise ValueError(f"Invalid skill name: {name!r}")
    if "/" in name or "\\" in name or name.startswith("."):
        raise ValueError(f"Unsafe skill name (path separators not allowed): {name!r}")
    target = (dest_dir / name).resolve()
    if target.parent != dest_dir.resolve():
        raise ValueError(f"Skill name escapes destination directory: {name!r}")
    return target


def _name_from_markdown(text: str, fallback: str) -> str:
    """Extract the frontmatter ``name`` from a whole-file SKILL.md, else *fallback*."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            meta = yaml.safe_load(text[3:end])
            if isinstance(meta, dict) and meta.get("name"):
                return str(meta["name"])
    return fallback


def _copy_decomposed_extras(src: Path, dest: Path) -> None:
    """Copy a decomposed skill's bundled files (e.g. references/), not its sources."""
    for item in src.iterdir():
        if item.name in _DECOMP_SOURCES or item.name in _DECOMP_DIRS:
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest / item.name)


def _materialize_skill(ref: str, dest_dir: Path, language: str | None) -> None:
    """Materialize a single skill ref into ``dest_dir/<name>/``."""
    src = _resolve_skill_ref(ref)

    # Single .md file -> whole-file skill.
    if src.is_file():
        if src.suffix != ".md":
            raise ValueError(f"Skill ref must be a directory or .md file: {ref!r}")
        text = src.read_text()
        out = _safe_skill_dirname(_name_from_markdown(text, src.stem), dest_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "SKILL.md").write_text(text)
        return

    # Decomposed skill -> render on demand, then copy bundled extras.
    if (src / "skill.yaml").is_file():
        meta = load_skill(src)
        out = _safe_skill_dirname(skill_name(meta, language), dest_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "SKILL.md").write_text(render(src, language))
        _copy_decomposed_extras(src, out)
        return

    # Whole-file skill -> copy the directory as-is.
    skill_md = src / "SKILL.md"
    if skill_md.is_file():
        name = _name_from_markdown(skill_md.read_text(), src.name)
        out = _safe_skill_dirname(name, dest_dir)
        shutil.copytree(src, out, dirs_exist_ok=True)
        return

    raise FileNotFoundError(f"No skill.yaml or SKILL.md in {src} (ref {ref!r})")


def materialize_skills(
    refs: list[str],
    dest_dir: Path | str,
    language: str | None = None,
) -> Path:
    """Materialize a list of skill refs into ``dest_dir`` for Harbor skill injection."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    for ref in refs:
        _materialize_skill(ref, dest_dir, language)
    return dest_dir


def materialize_treatment(
    name: str,
    dest_dir: Path | str,
    language: str | None = None,
    repo_root: Path | str | None = None,
) -> Path:
    """Materialize a named treatment's skills into ``dest_dir``.

    Writes one ``<skill-name>/SKILL.md`` folder per skill — the agent-agnostic layout
    Harbor injects via ``--skills``. CONTROL and any skill-less treatment produce an
    empty directory.

    Args:
        name: Treatment name (e.g. "CONTROL", "ALL_MAIN_SKILLS").
        dest_dir: Host directory to write the skill tree into (created if needed).
        language: 'py' | 'ts' | None — render axis for decomposed skills.
        repo_root: Optional repo root override (else env / auto-discovery).

    Returns:
        The destination directory path.
    """
    if repo_root is not None:
        _set_repo_root(Path(repo_root))

    configs = load_treatments()
    if name not in configs:
        raise KeyError(f"Treatment not found: {name}. Available: {sorted(configs)}")

    return materialize_skills(configs[name].skills, dest_dir, language)


def _set_repo_root(root: Path) -> None:
    """Rebind module-level skill/treatment base paths to *root* (packaged deploys)."""
    global _ROOT, TREATMENTS_FOLDER, SKILLS_ROOT
    _ROOT = root.resolve()
    TREATMENTS_FOLDER = _ROOT / "treatments"
    SKILLS_ROOT = _ROOT / "skills"
