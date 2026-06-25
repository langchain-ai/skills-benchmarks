#!/usr/bin/env python3
"""Convert a legacy XML-tagged skill into the decomposed file-per-section layout.

Reads `<skill_dir>/skill_all.md` (the both-languages source of truth), splits its
top-level `<tag>...</tag>` blocks into `sections/<tag>.md`, and for example blocks
that wrap `<python>` / `<typescript>` writes `sections/<tag>.py.md` / `.ts.md`. The
frontmatter becomes skill.yaml (name, description, ordered sections, and per-language
names harvested from skill_py.md / skill_ts.md when they differ).

Usage:
    uv run python scripts/convert_skill.py skills/benchmarks/oss_split/lc_streaming
"""

import argparse
import re
from pathlib import Path

import yaml

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
_SAFE_TAG = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_TOP_TAG = re.compile(r"<([A-Za-z][A-Za-z0-9_-]*)>")


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (fields, body). Frontmatter is parsed line-by-line rather than via a
    YAML loader: legacy skills have unquoted descriptions containing ``: `` that a
    strict YAML parser rejects, and flat key/value lines need no deserialization."""
    m = _FRONTMATTER.match(text)
    if not m:
        raise ValueError("skill_all.md has no leading frontmatter block")
    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, val = line.partition(":")
        if not sep:
            continue
        val = val.strip()
        if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
            val = val[1:-1]
        fields[key.strip()] = val
    return fields, text[m.end():]


def _inner_block(body: str, tag: str, start: int) -> tuple[str, int] | None:
    """Return (inner_text, end_index_after_close) for the first <tag> at/after start."""
    open_tag, close_tag = f"<{tag}>", f"</{tag}>"
    open_at = body.find(open_tag, start)
    if open_at == -1:
        return None
    inner_start = open_at + len(open_tag)
    close_at = body.find(close_tag, inner_start)
    if close_at == -1:
        raise ValueError(f"unterminated <{tag}> block")
    return body[inner_start:close_at].strip(), close_at + len(close_tag)


def _top_level_blocks(body: str) -> list[tuple[str, str]]:
    """Ordered (tag, inner_text) for each top-level tag (nested lang tags skipped)."""
    blocks: list[tuple[str, str]] = []
    pos = 0
    while (m := _TOP_TAG.search(body, pos)) is not None:
        tag = m.group(1)
        if not _SAFE_TAG.match(tag):
            raise ValueError(f"unsafe tag name: {tag!r}")
        result = _inner_block(body, tag, m.start())
        if result is None:
            break
        inner, pos = result
        blocks.append((tag, inner))
    return blocks


def _write_section(sections_dir: Path, name: str, content: str) -> None:
    # Confine every write to sections/ — reject any traversal in the derived name.
    target = (sections_dir / name).resolve()
    if not str(target).startswith(str(sections_dir.resolve()) + "/"):
        raise ValueError(f"refusing to write outside sections dir: {name!r}")
    target.write_text(content.rstrip() + "\n")


def _language_names(skill_dir: Path, all_name: str) -> dict[str, str]:
    names: dict[str, str] = {}
    for lang, variant_file in (("py", "skill_py.md"), ("ts", "skill_ts.md")):
        path = skill_dir / variant_file
        if not path.is_file():
            continue
        meta, _ = _split_frontmatter(path.read_text())
        if (name := meta.get("name")) and name != all_name:
            names[lang] = name
    return names


def _clear_sections(sections_dir: Path) -> None:
    """Remove existing *.md files in sections/ so re-runs don't leave stale files."""
    sections_dir = sections_dir.resolve()
    if not sections_dir.is_dir():
        return
    for f in sections_dir.glob("*.md"):
        if f.resolve().parent == sections_dir:  # confine to this dir
            f.unlink()


def _has_nested_lang(body: str) -> bool:
    """True if any top-level block wraps a <python>/<typescript> block (oss pattern)."""
    return any(
        _inner_block(inner, "python", 0) or _inner_block(inner, "typescript", 0)
        for _tag, inner in _top_level_blocks(body)
    )


def _convert_from_all(sections_dir: Path, body: str) -> list[str]:
    """Mode 1 (oss): split each top-level block; nested lang blocks become variants."""
    order: list[str] = []
    for tag, inner in _top_level_blocks(body):
        py = _inner_block(inner, "python", 0)
        ts = _inner_block(inner, "typescript", 0)
        if py or ts:
            if py:
                _write_section(sections_dir, f"{tag}.py.md", py[0])
            if ts:
                _write_section(sections_dir, f"{tag}.ts.md", ts[0])
        else:
            _write_section(sections_dir, f"{tag}.md", inner)
        order.append(tag)
    return order


def _convert_from_variants(sections_dir: Path, py_text: str, ts_text: str) -> list[str]:
    """Mode 2 (langsmith): per-section diff of the py and ts files.

    Sections identical across languages are single-sourced (`<tag>.md`); sections
    that differ become `<tag>.py.md` + `<tag>.ts.md`; single-language sections get
    just their one variant.
    """
    py_blocks = _top_level_blocks(_split_frontmatter(py_text)[1])
    ts_blocks = _top_level_blocks(_split_frontmatter(ts_text)[1])
    py_map, ts_map = dict(py_blocks), dict(ts_blocks)
    order = [tag for tag, _ in py_blocks]
    order += [tag for tag, _ in ts_blocks if tag not in py_map]
    for tag in order:
        p, t = py_map.get(tag), ts_map.get(tag)
        if p is not None and t is not None and p == t:
            _write_section(sections_dir, f"{tag}.md", p)
        else:
            if p is not None:
                _write_section(sections_dir, f"{tag}.py.md", p)
            if t is not None:
                _write_section(sections_dir, f"{tag}.ts.md", t)
    return order


def convert(skill_dir: Path) -> None:
    skill_dir = Path(skill_dir)
    meta, all_body = _split_frontmatter((skill_dir / "skill_all.md").read_text())
    sections_dir = skill_dir / "sections"
    _clear_sections(sections_dir)
    sections_dir.mkdir(exist_ok=True)

    py_file, ts_file = skill_dir / "skill_py.md", skill_dir / "skill_ts.md"
    if not _has_nested_lang(all_body) and py_file.is_file() and ts_file.is_file():
        mode = "py/ts-diff"
        order = _convert_from_variants(sections_dir, py_file.read_text(), ts_file.read_text())
    else:
        mode = "skill_all"
        order = _convert_from_all(sections_dir, all_body)

    skill_yaml = {"name": meta["name"], "description": meta.get("description", "")}
    if lang_names := _language_names(skill_dir, meta["name"]):
        skill_yaml["language_names"] = lang_names
    skill_yaml["sections"] = order
    (skill_dir / "skill.yaml").write_text(
        yaml.safe_dump(skill_yaml, sort_keys=False, allow_unicode=True, width=10**9)
    )
    print(f"[{mode}] Wrote {skill_dir}/skill.yaml + {len(order)} sections "
          f"({len(list(sections_dir.glob('*.md')))} files)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path, help="Skill directory containing skill_all.md")
    convert(parser.parse_args().skill_dir)


if __name__ == "__main__":
    main()
