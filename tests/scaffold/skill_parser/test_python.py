"""Unit tests for skill_parser module.

Tests cover:
- Section parsing and extraction
- Language variant loading
- Tag stripping and filtering
- Skill configuration building

Tests also verify that incorrect implementations would fail by testing edge cases.
"""


import pytest

from scaffold.python.skill_parser import (
    format_section_with_tags,
    get_section_list,
    load_skill,
    load_skill_content,
    load_skill_variant,
    parse_skill_md,
    parse_skill_md_ordered,
    skill_config,
    split_skill,
    strip_by_tags,
    strip_lang_tags,
)

# =============================================================================
# FIXTURES
# =============================================================================

BASIC_SKILL_MD = """---
name: test-skill
description: "A test skill for unit testing"
---

<overview>
This is the overview section.
It has multiple lines.
</overview>

<setup>
Setup instructions here.
</setup>

<ex_basic>
Basic example content.
</ex_basic>
"""

SKILL_WITH_LANG_TAGS = """---
name: multi-lang-skill
description: "Skill with language-specific content"
---

<overview>
Common overview.
</overview>

<examples>
<python>
def hello():
    print("Hello from Python")
</python>

<typescript>
function hello() {
    console.log("Hello from TypeScript");
}
</typescript>
</examples>
"""

SKILL_WITH_TAG_ATTRS = """---
name: tagged-skill
description: "Skill with tag attributes"
---

<examples>
<python tag="basic">
Basic Python example
</python>

<python tag="advanced">
Advanced Python example
</python>

<typescript tag="basic">
Basic TypeScript example
</typescript>
</examples>
"""


@pytest.fixture
def basic_skill_dir(tmp_path):
    """Create a basic skill directory."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "skill.md").write_text(BASIC_SKILL_MD)
    return skill_dir


@pytest.fixture
def skill_with_variants(tmp_path):
    """Create a skill directory with variant files."""
    skill_dir = tmp_path / "multi-skill"
    skill_dir.mkdir()

    # Main skill.md
    (skill_dir / "skill.md").write_text(BASIC_SKILL_MD)

    # Python variant
    (skill_dir / "skill_py.md").write_text("""---
name: test-skill
description: "Python variant"
---

<overview>
Python-specific overview.
</overview>
""")

    # TypeScript variant
    (skill_dir / "skill_ts.md").write_text("""---
name: test-skill
description: "TypeScript variant"
---

<overview>
TypeScript-specific overview.
</overview>
""")

    # All variant
    (skill_dir / "skill_all.md").write_text(SKILL_WITH_LANG_TAGS)

    # Scripts directory
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "example.py").write_text("# Python script")
    (scripts_dir / "example.ts").write_text("// TypeScript script")

    return skill_dir


@pytest.fixture
def lang_skill_file(tmp_path):
    """Create a skill file with language tags."""
    skill_file = tmp_path / "skill.md"
    skill_file.write_text(SKILL_WITH_LANG_TAGS)
    return skill_file


@pytest.fixture
def tagged_skill_file(tmp_path):
    """Create a skill file with tag attributes."""
    skill_file = tmp_path / "skill.md"
    skill_file.write_text(SKILL_WITH_TAG_ATTRS)
    return skill_file


# =============================================================================
# parse_skill_md TESTS
# =============================================================================


class TestParseSkillMd:
    def test_extracts_frontmatter(self, basic_skill_dir):
        """Verify frontmatter is extracted with --- delimiters."""
        sections = parse_skill_md(basic_skill_dir / "skill.md")

        assert "frontmatter" in sections
        assert "name: test-skill" in sections["frontmatter"]
        assert sections["frontmatter"].startswith("---")
        assert sections["frontmatter"].endswith("---")

    def test_extracts_xml_sections(self, basic_skill_dir):
        """Verify XML sections are extracted correctly."""
        sections = parse_skill_md(basic_skill_dir / "skill.md")

        assert "overview" in sections
        assert "setup" in sections
        assert "ex_basic" in sections

    def test_preserves_xml_tags_by_default(self, basic_skill_dir):
        """Verify XML tags are preserved when keep_tags=True (default)."""
        sections = parse_skill_md(basic_skill_dir / "skill.md")

        assert sections["overview"].startswith("<overview>")
        assert sections["overview"].endswith("</overview>")

    def test_strips_xml_tags_when_requested(self, basic_skill_dir):
        """Verify XML tags are stripped when keep_tags=False."""
        sections = parse_skill_md(basic_skill_dir / "skill.md", keep_tags=False)

        assert not sections["overview"].startswith("<overview>")
        assert "This is the overview section" in sections["overview"]

    def test_handles_multiline_content(self, basic_skill_dir):
        """Verify multiline section content is preserved."""
        sections = parse_skill_md(basic_skill_dir / "skill.md")

        assert "multiple lines" in sections["overview"]

    def test_returns_empty_dict_for_empty_file(self, tmp_path):
        """Verify empty file returns empty dict."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")

        sections = parse_skill_md(empty_file)
        assert sections == {}

    def test_handles_missing_frontmatter(self, tmp_path):
        """Verify skill without frontmatter still parses sections."""
        no_frontmatter = tmp_path / "skill.md"
        no_frontmatter.write_text("<overview>\nContent here\n</overview>")

        sections = parse_skill_md(no_frontmatter)
        assert "frontmatter" not in sections
        assert "overview" in sections


class TestParseSkillMdOrdered:
    def test_preserves_section_order(self, basic_skill_dir):
        """Verify sections are returned in document order."""
        sections = parse_skill_md_ordered(basic_skill_dir / "skill.md")

        tags = [tag for tag, _ in sections]
        assert tags == ["frontmatter", "overview", "setup", "ex_basic"]

    def test_returns_tuples(self, basic_skill_dir):
        """Verify return type is list of (tag, content) tuples."""
        sections = parse_skill_md_ordered(basic_skill_dir / "skill.md")

        assert isinstance(sections, list)
        assert all(isinstance(s, tuple) and len(s) == 2 for s in sections)


# =============================================================================
# get_section_list TESTS
# =============================================================================


class TestGetSectionList:
    def test_returns_all_sections_in_order(self, basic_skill_dir):
        """Verify all sections are returned in document order."""
        sections = get_section_list(basic_skill_dir / "skill.md")

        assert len(sections) == 4  # frontmatter, overview, setup, ex_basic
        assert "---" in sections[0]  # frontmatter first
        assert "<overview>" in sections[1]

    def test_excludes_specified_tags(self, basic_skill_dir):
        """Verify excluded tags are filtered out."""
        sections = get_section_list(
            basic_skill_dir / "skill.md", exclude_tags=["frontmatter"]
        )

        assert len(sections) == 3
        assert not any("---" in s for s in sections if not s.startswith("<"))

    def test_exclude_multiple_tags(self, basic_skill_dir):
        """Verify multiple tags can be excluded."""
        sections = get_section_list(
            basic_skill_dir / "skill.md", exclude_tags=["frontmatter", "setup"]
        )

        assert len(sections) == 2
        # Only overview and ex_basic should remain
        content = "\n".join(sections)
        assert "<overview>" in content
        assert "<ex_basic>" in content
        assert "<setup>" not in content


# =============================================================================
# load_skill TESTS
# =============================================================================


class TestLoadSkill:
    def test_loads_sections_dict(self, basic_skill_dir):
        """Verify sections are loaded as dict."""
        skill = load_skill(basic_skill_dir)

        assert "sections" in skill
        assert isinstance(skill["sections"], dict)
        assert "overview" in skill["sections"]

    def test_loads_all_sections_list(self, basic_skill_dir):
        """Verify all sections are loaded as list."""
        skill = load_skill(basic_skill_dir)

        assert "all" in skill
        assert isinstance(skill["all"], list)
        assert len(skill["all"]) == 4

    def test_detects_scripts_dir(self, skill_with_variants):
        """Verify scripts directory is detected."""
        skill = load_skill(skill_with_variants)

        assert skill["scripts_dir"] is not None
        assert skill["scripts_dir"].exists()

    def test_handles_missing_scripts_dir(self, basic_skill_dir):
        """Verify missing scripts dir returns None."""
        skill = load_skill(basic_skill_dir)

        assert skill["scripts_dir"] is None


# =============================================================================
# load_skill_variant TESTS
# =============================================================================


class TestLoadSkillVariant:
    def test_loads_python_variant(self, skill_with_variants):
        """Verify Python variant is loaded."""
        skill = load_skill_variant(skill_with_variants, "py")

        assert "Python-specific overview" in skill["sections"]["overview"]

    def test_loads_typescript_variant(self, skill_with_variants):
        """Verify TypeScript variant is loaded."""
        skill = load_skill_variant(skill_with_variants, "ts")

        assert "TypeScript-specific overview" in skill["sections"]["overview"]

    def test_loads_all_variant(self, skill_with_variants):
        """Verify all variant is loaded with both languages."""
        skill = load_skill_variant(skill_with_variants, "all")

        examples = skill["sections"].get("examples", "")
        assert "<python>" in examples
        assert "<typescript>" in examples

    def test_loads_default_without_variant(self, skill_with_variants):
        """Verify default skill.md is loaded when variant is None."""
        skill = load_skill_variant(skill_with_variants, None)

        assert "This is the overview section" in skill["sections"]["overview"]

    def test_sets_script_filter(self, skill_with_variants):
        """Verify script_filter is set from variant."""
        skill_py = load_skill_variant(skill_with_variants, "py")
        skill_ts = load_skill_variant(skill_with_variants, "ts")

        assert skill_py["script_filter"] == "py"
        assert skill_ts["script_filter"] == "ts"

    def test_raises_for_missing_variant(self, basic_skill_dir):
        """Verify error is raised for missing variant file."""
        with pytest.raises(FileNotFoundError):
            load_skill_variant(basic_skill_dir, "py")


# =============================================================================
# strip_lang_tags TESTS
# =============================================================================


class TestStripLangTags:
    def test_removes_python_tags(self, lang_skill_file):
        """Verify Python tags are removed."""
        content = load_skill_content(lang_skill_file)
        result = strip_lang_tags(content, exclude=["python"])

        assert "<python>" not in result
        assert "</python>" not in result
        assert "print(" not in result
        # TypeScript should remain
        assert "<typescript>" in result
        assert "console.log" in result

    def test_removes_typescript_tags(self, lang_skill_file):
        """Verify TypeScript tags are removed."""
        content = load_skill_content(lang_skill_file)
        result = strip_lang_tags(content, exclude=["typescript"])

        assert "<typescript>" not in result
        assert "</typescript>" not in result
        assert "console.log" not in result
        # Python should remain
        assert "<python>" in result
        assert "print(" in result

    def test_removes_both_languages(self, lang_skill_file):
        """Verify both language tags can be removed."""
        content = load_skill_content(lang_skill_file)
        result = strip_lang_tags(content, exclude=["python", "typescript"])

        assert "<python>" not in result
        assert "<typescript>" not in result

    def test_preserves_content_with_empty_exclude(self, lang_skill_file):
        """Verify content is unchanged with empty exclude list."""
        content = load_skill_content(lang_skill_file)
        result = strip_lang_tags(content, exclude=[])

        assert result == content

    def test_preserves_content_with_none_exclude(self, lang_skill_file):
        """Verify content is unchanged with None exclude."""
        content = load_skill_content(lang_skill_file)
        result = strip_lang_tags(content, exclude=None)

        assert result == content

    def test_cleans_up_blank_lines(self, lang_skill_file):
        """Verify excessive blank lines are cleaned up."""
        content = load_skill_content(lang_skill_file)
        result = strip_lang_tags(content, exclude=["python"])

        # Should not have more than 2 consecutive newlines
        assert "\n\n\n" not in result


# =============================================================================
# strip_by_tags TESTS
# =============================================================================


class TestStripByTags:
    def test_removes_tagged_python_block(self, tagged_skill_file):
        """Verify specific tagged Python block is removed."""
        content = load_skill_content(tagged_skill_file)
        result = strip_by_tags(content, exclude=["basic"])

        assert "Basic Python example" not in result
        assert "Basic TypeScript example" not in result
        # Advanced should remain
        assert "Advanced Python example" in result

    def test_removes_only_matching_tag(self, tagged_skill_file):
        """Verify only exact tag match is removed."""
        content = load_skill_content(tagged_skill_file)
        result = strip_by_tags(content, exclude=["advanced"])

        assert "Advanced Python example" not in result
        # Basic should remain
        assert "Basic Python example" in result
        assert "Basic TypeScript example" in result

    def test_preserves_untagged_content(self, tagged_skill_file):
        """Verify content without tag attrs is preserved."""
        content = load_skill_content(tagged_skill_file)
        result = strip_by_tags(content, exclude=["nonexistent"])

        # All content should remain
        assert "Basic Python example" in result
        assert "Advanced Python example" in result


# =============================================================================
# skill_config TESTS
# =============================================================================


class TestSkillConfig:
    def test_creates_config_dict(self):
        """Verify skill_config creates proper dict structure."""
        config = skill_config(["section1", "section2"])

        assert "sections" in config
        assert config["sections"] == ["section1", "section2"]
        assert config["scripts_dir"] is None
        assert config["script_filter"] is None

    def test_includes_scripts_dir(self, tmp_path):
        """Verify scripts_dir is included."""
        scripts = tmp_path / "scripts"
        scripts.mkdir()

        config = skill_config(["section"], scripts_dir=scripts)

        assert config["scripts_dir"] == scripts

    def test_includes_script_filter(self):
        """Verify script_filter is included."""
        config = skill_config(["section"], script_filter="py")

        assert config["script_filter"] == "py"


# =============================================================================
# split_skill TESTS
# =============================================================================


class TestSplitSkill:
    def test_splits_by_section_tags(self, basic_skill_dir):
        """Verify skill is split into multiple configs."""
        skill = load_skill(basic_skill_dir)
        splits = split_skill(
            skill,
            {
                "skill-overview": ["frontmatter", "overview"],
                "skill-setup": ["frontmatter", "setup"],
            },
        )

        assert "skill-overview" in splits
        assert "skill-setup" in splits
        assert len(splits["skill-overview"]["sections"]) == 2
        assert len(splits["skill-setup"]["sections"]) == 2

    def test_preserves_scripts_dir(self, skill_with_variants):
        """Verify scripts_dir is preserved in splits."""
        skill = load_skill(skill_with_variants)
        splits = split_skill(skill, {"split1": ["overview"]})

        assert splits["split1"]["scripts_dir"] == skill["scripts_dir"]


# =============================================================================
# format_section_with_tags TESTS
# =============================================================================


class TestFormatSectionWithTags:
    def test_formats_with_tags(self):
        """Verify content is wrapped with XML tags."""
        result = format_section_with_tags("overview", "This is content.")

        assert result == "<overview>\nThis is content.\n</overview>"

    def test_handles_multiline_content(self):
        """Verify multiline content is formatted correctly."""
        content = "Line 1\nLine 2\nLine 3"
        result = format_section_with_tags("test", content)

        assert result.startswith("<test>\n")
        assert result.endswith("\n</test>")
        assert "Line 1\nLine 2\nLine 3" in result


# =============================================================================
# REGRESSION TESTS - Verify incorrect implementations would fail
# =============================================================================


class TestRegressionCases:
    """Tests that would fail if implementation is broken."""

    def test_frontmatter_uses_dashes_not_xml(self, tmp_path):
        """Verify frontmatter is extracted via --- not <frontmatter> tags."""
        # This tests that we correctly handle YAML frontmatter format
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""---
name: test
---

<overview>
Content
</overview>
""")
        sections = parse_skill_md(skill_file)

        # Frontmatter should start with ---
        assert sections["frontmatter"].startswith("---")
        # And should contain the name
        assert "name: test" in sections["frontmatter"]

    def test_nested_tags_not_confused(self, tmp_path):
        """Verify nested XML-like content doesn't break parsing."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""<examples>
Here is some <code>inline code</code> text.
</examples>
""")
        sections = parse_skill_md(skill_file)

        # Should parse examples section, not get confused by <code>
        assert "examples" in sections
        assert "<code>inline code</code>" in sections["examples"]

    def test_section_order_matters(self, tmp_path):
        """Verify section order is preserved (important for skill composition)."""
        skill_file = tmp_path / "skill.md"
        # Deliberately use non-alphabetical order to catch sorting bugs
        skill_file.write_text("""<zebra>
First
</zebra>

<apple>
Second
</apple>

<mango>
Third
</mango>
""")
        sections = parse_skill_md_ordered(skill_file)
        tags = [tag for tag, _ in sections]

        # Order must be preserved - this is critical for skill file structure
        # If sorted alphabetically, would be ["apple", "mango", "zebra"]
        assert tags == ["zebra", "apple", "mango"]

    def test_strip_lang_handles_attributes(self, tmp_path):
        """Verify strip_lang_tags handles tags with attributes."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""<examples>
<python tag="test">
Python code
</python>
</examples>
""")
        content = skill_file.read_text()
        result = strip_lang_tags(content, exclude=["python"])

        # Tag with attribute should be removed
        assert "Python code" not in result
        assert "<python" not in result

    def test_exclude_list_not_mutated(self, lang_skill_file):
        """Verify exclude lists are not mutated during processing."""
        content = load_skill_content(lang_skill_file)
        exclude = ["python"]
        original = exclude.copy()

        strip_lang_tags(content, exclude=exclude)

        assert exclude == original  # List should not be modified

    def test_empty_sections_handled(self, tmp_path):
        """Verify empty sections don't cause errors."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""<empty>
</empty>

<nonempty>
Has content
</nonempty>
""")
        sections = parse_skill_md(skill_file)

        assert "empty" in sections
        assert "nonempty" in sections

    def test_special_characters_in_content(self, tmp_path):
        """Verify special regex characters in content don't break parsing."""
        skill_file = tmp_path / "skill.md"
        skill_file.write_text("""<code>
regex = r"\\d+\\.\\d+"
path = "C:\\Users\\test"
url = "https://example.com?foo=bar&baz=qux"
</code>
""")
        sections = parse_skill_md(skill_file)

        assert "code" in sections
        assert r"\d+" in sections["code"]
        assert "C:\\Users" in sections["code"]
