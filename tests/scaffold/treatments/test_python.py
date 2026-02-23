"""Unit tests for treatments module.

Tests cover:
- Treatment loading from YAML
- Skill configuration building
- Noise task building
- Treatment listing

Tests mirror TypeScript test_treatments.test.ts for parity.
"""

import pytest

from scaffold.python.treatments import (
    TreatmentConfig,
    build_treatment_skills,
    list_treatments,
    load_treatments,
    load_treatments_yaml,
)

# =============================================================================
# FIXTURES
# =============================================================================

BASIC_TREATMENT_YAML = """
CONTROL:
  description: "Control treatment with no skills"
  skills: []

BASIC_SKILL:
  description: "Treatment with basic skill"
  skills:
    - skill: test_skill
      variant: py

MULTI_SKILL:
  description: "Treatment with multiple skills"
  skills:
    - skill: skill_a
      name: skill-a
    - skill: skill_b
      name: skill-b
"""

TREATMENT_WITH_ANCHORS = """
_common_section: &common |
  Common content

TREATMENT_A:
  description: "Uses anchor"
  skills:
    - skill: test_skill
      extra_sections:
        - *common
"""


@pytest.fixture
def treatments_yaml_file(tmp_path):
    """Create a temporary treatments YAML file."""
    yaml_file = tmp_path / "treatments.yaml"
    yaml_file.write_text(BASIC_TREATMENT_YAML)
    return yaml_file


@pytest.fixture
def anchors_yaml_file(tmp_path):
    """Create a YAML file with anchors."""
    yaml_file = tmp_path / "anchors.yaml"
    yaml_file.write_text(TREATMENT_WITH_ANCHORS)
    return yaml_file


@pytest.fixture
def mock_skill_dir(tmp_path):
    """Create a mock skill directory."""
    skill_dir = tmp_path / "skills" / "benchmarks" / "test_skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.md").write_text("""---
name: test-skill
description: "A test skill"
---

<overview>
Test skill overview.
</overview>
""")
    (skill_dir / "skill_py.md").write_text("""---
name: test-skill
description: "Python variant"
---

<overview>
Python-specific content.
</overview>
""")
    return skill_dir


# =============================================================================
# load_treatments_yaml TESTS
# =============================================================================


class TestLoadTreatmentsYaml:
    def test_loads_treatments_from_yaml(self, treatments_yaml_file):
        """Verify treatments are loaded from YAML file."""
        treatments = load_treatments_yaml(treatments_yaml_file)

        assert "CONTROL" in treatments
        assert "BASIC_SKILL" in treatments
        assert "MULTI_SKILL" in treatments

    def test_parses_treatment_description(self, treatments_yaml_file):
        """Verify treatment description is parsed."""
        treatments = load_treatments_yaml(treatments_yaml_file)

        assert treatments["CONTROL"].description == "Control treatment with no skills"

    def test_parses_skills_configuration(self, treatments_yaml_file):
        """Verify skills configuration is parsed."""
        treatments = load_treatments_yaml(treatments_yaml_file)

        assert len(treatments["BASIC_SKILL"].skills) == 1
        assert treatments["BASIC_SKILL"].skills[0]["skill"] == "test_skill"
        assert treatments["BASIC_SKILL"].skills[0]["variant"] == "py"

    def test_raises_for_missing_file(self, tmp_path):
        """Verify error for missing file."""
        with pytest.raises(FileNotFoundError):
            load_treatments_yaml(tmp_path / "nonexistent.yaml")

    def test_skips_yaml_anchors(self, anchors_yaml_file):
        """Verify YAML anchors (keys starting with _) are skipped."""
        treatments = load_treatments_yaml(anchors_yaml_file)

        assert "_common_section" not in treatments
        assert "TREATMENT_A" in treatments


# =============================================================================
# load_treatments TESTS
# =============================================================================


class TestLoadTreatments:
    def test_loads_treatments_from_folder(self):
        """Verify treatments are loaded from real treatments folder."""
        treatments = load_treatments()

        # Should have at least some treatments
        assert len(treatments) > 0

    def test_returns_treatment_config_objects(self):
        """Verify TreatmentConfig objects are returned."""
        treatments = load_treatments()
        names = list(treatments.keys())

        if names:
            treatment = treatments[names[0]]
            assert isinstance(treatment, TreatmentConfig)
            assert hasattr(treatment, "name")
            assert hasattr(treatment, "description")


# =============================================================================
# list_treatments TESTS
# =============================================================================


class TestListTreatments:
    def test_returns_list_of_names(self):
        """Verify list of treatment names is returned."""
        names = list_treatments()

        assert isinstance(names, list)
        assert len(names) > 0


# =============================================================================
# build_treatment_skills TESTS
# =============================================================================


class TestBuildTreatmentSkills:
    def test_returns_empty_for_empty_input(self):
        """Verify empty dict for empty input."""
        skills = build_treatment_skills([])

        assert skills == {}

    def test_handles_inline_content(self):
        """Verify inline content is handled."""
        configs = [{"name": "custom-skill", "content": "Custom skill content here"}]

        skills = build_treatment_skills(configs)

        assert "custom-skill" in skills
        assert "Custom skill content here" in skills["custom-skill"]["sections"][0]

    def test_generates_name_from_skill_directory(self):
        """Verify name is generated from skill directory with underscores replaced."""
        configs = [{"skill": "my_skill_name", "content": "Some content"}]

        skills = build_treatment_skills(configs)

        # Should convert underscores to dashes
        assert "my-skill-name" in skills

    def test_uses_specified_name_over_generated(self):
        """Verify specified name is used over generated."""
        configs = [
            {"skill": "my_skill_name", "name": "override-name", "content": "Some content"}
        ]

        skills = build_treatment_skills(configs)

        assert "override-name" in skills
        assert "my-skill-name" not in skills


# =============================================================================
# REGRESSION TESTS - Verify incorrect implementations would fail
# =============================================================================


class TestRegressionCases:
    def test_skill_name_conversion_uses_dashes(self):
        """Verify skill name conversion uses dashes not underscores."""
        configs = [{"skill": "snake_case_skill", "content": "content"}]

        skills = build_treatment_skills(configs)

        # Must be snake-case-skill, NOT snake_case_skill
        assert "snake-case-skill" in skills
        assert "snake_case_skill" not in skills

    def test_yaml_anchors_not_included(self, anchors_yaml_file):
        """Verify YAML anchors are not included as treatments."""
        treatments = load_treatments_yaml(anchors_yaml_file)

        # Only TREATMENT_A should be present, not _common_section
        assert list(treatments.keys()) == ["TREATMENT_A"]

    def test_empty_skills_array_does_not_crash(self, treatments_yaml_file):
        """Verify empty skills array doesn't crash."""
        treatments = load_treatments_yaml(treatments_yaml_file)
        control = treatments["CONTROL"]

        assert control.skills == []

        # Building skills should return empty dict
        skills = build_treatment_skills(control.skills)
        assert skills == {}

    def test_treatment_config_preserves_all_fields(self, tmp_path):
        """Verify all TreatmentConfig fields are preserved."""
        yaml_file = tmp_path / "full.yaml"
        yaml_file.write_text("""
FULL_TREATMENT:
  description: "Full treatment"
  claude_md: "Custom CLAUDE.md content"
  skills:
    - skill: test_skill
      variant: py
  noise_tasks:
    - EMOJI
""")

        treatments = load_treatments_yaml(yaml_file)
        treatment = treatments["FULL_TREATMENT"]

        assert treatment.description == "Full treatment"
        assert treatment.claude_md == "Custom CLAUDE.md content"
        assert len(treatment.skills) == 1
        assert treatment.noise_tasks == ["EMOJI"]

    def test_multi_skill_treatment_preserves_order(self, treatments_yaml_file):
        """Verify multiple skills preserve order."""
        treatments = load_treatments_yaml(treatments_yaml_file)
        multi = treatments["MULTI_SKILL"]

        assert len(multi.skills) == 2
        assert multi.skills[0]["skill"] == "skill_a"
        assert multi.skills[1]["skill"] == "skill_b"
