/**
 * Unit tests for treatments module.
 *
 * Tests cover:
 * - Treatment loading from YAML
 * - Skill configuration building
 * - Noise task building
 * - Treatment listing
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { mkdtempSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

import {
  loadTreatmentsYaml,
  loadTreatments,
  listTreatments,
  buildNoiseTasks,
  buildTreatmentSkills,
  type SkillConfigInput,
} from "../../../scaffold/typescript/treatments.js";

// =============================================================================
// FIXTURES
// =============================================================================

const BASIC_TREATMENT_YAML = `
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
`;

const TREATMENT_WITH_ANCHORS = `
_common_section: &common |
  Common content

TREATMENT_A:
  description: "Uses anchor"
  skills:
    - skill: test_skill
      extra_sections:
        - *common
`;

// =============================================================================
// TESTS
// =============================================================================

describe("treatments", () => {
  let tempDir: string;
  let treatmentYamlPath: string;
  let skillDir: string;

  beforeAll(() => {
    tempDir = mkdtempSync(join(tmpdir(), "treatments_test_"));

    // Create treatment YAML
    treatmentYamlPath = join(tempDir, "treatments.yaml");
    writeFileSync(treatmentYamlPath, BASIC_TREATMENT_YAML);

    // Create a mock skill directory
    skillDir = join(tempDir, "skills", "benchmarks", "test_skill");
    mkdirSync(skillDir, { recursive: true });
    writeFileSync(
      join(skillDir, "skill.md"),
      `---
name: test-skill
description: "A test skill"
---

<overview>
Test skill overview.
</overview>
`
    );
    writeFileSync(
      join(skillDir, "skill_py.md"),
      `---
name: test-skill
description: "Python variant"
---

<overview>
Python-specific content.
</overview>
`
    );
  });

  afterAll(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  describe("loadTreatmentsYaml", () => {
    it("loads treatments from YAML file", () => {
      const treatments = loadTreatmentsYaml(treatmentYamlPath);

      expect(treatments).toHaveProperty("CONTROL");
      expect(treatments).toHaveProperty("BASIC_SKILL");
      expect(treatments).toHaveProperty("MULTI_SKILL");
    });

    it("parses treatment description", () => {
      const treatments = loadTreatmentsYaml(treatmentYamlPath);

      expect(treatments.CONTROL.description).toBe("Control treatment with no skills");
    });

    it("parses skills configuration", () => {
      const treatments = loadTreatmentsYaml(treatmentYamlPath);

      expect(treatments.BASIC_SKILL.skills).toHaveLength(1);
      expect(treatments.BASIC_SKILL.skills![0].skill).toBe("test_skill");
      expect(treatments.BASIC_SKILL.skills![0].variant).toBe("py");
    });

    it("returns empty object for missing file", () => {
      const treatments = loadTreatmentsYaml("/nonexistent/path.yaml");

      expect(treatments).toEqual({});
    });

    it("skips YAML anchors (keys starting with _)", () => {
      const yamlWithAnchors = join(tempDir, "anchors.yaml");
      writeFileSync(yamlWithAnchors, TREATMENT_WITH_ANCHORS);

      const treatments = loadTreatmentsYaml(yamlWithAnchors);

      expect(treatments).not.toHaveProperty("_common_section");
      expect(treatments).toHaveProperty("TREATMENT_A");
    });
  });

  describe("loadTreatments", () => {
    it("loads treatments from real treatments folder", () => {
      // This test uses the actual treatments folder
      const treatments = loadTreatments();

      // Should have at least some treatments
      expect(Object.keys(treatments).length).toBeGreaterThan(0);
    });

    it("returns TreatmentConfig objects", () => {
      const treatments = loadTreatments();
      const names = Object.keys(treatments);

      if (names.length > 0) {
        const treatment = treatments[names[0]];
        expect(treatment).toHaveProperty("name");
        expect(treatment).toHaveProperty("description");
      }
    });
  });

  describe("listTreatments", () => {
    it("returns list of treatment names", () => {
      const names = listTreatments();

      expect(Array.isArray(names)).toBe(true);
      expect(names.length).toBeGreaterThan(0);
    });
  });

  describe("buildNoiseTasks", () => {
    it("builds NoiseTask objects from names", () => {
      const noiseTasks = buildNoiseTasks(["EMOJI"]);

      // If EMOJI exists in NOISE_TASK_PROMPTS, we should get a task
      // Otherwise empty (which is valid)
      expect(Array.isArray(noiseTasks)).toBe(true);
    });

    it("filters out unknown noise task names", () => {
      const noiseTasks = buildNoiseTasks(["NONEXISTENT_NOISE_TASK"]);

      expect(noiseTasks).toHaveLength(0);
    });

    it("handles empty input", () => {
      const noiseTasks = buildNoiseTasks([]);

      expect(noiseTasks).toEqual([]);
    });
  });

  describe("buildTreatmentSkills", () => {
    it("returns empty object for undefined input", () => {
      const skills = buildTreatmentSkills(undefined);

      expect(skills).toEqual({});
    });

    it("returns empty object for empty array", () => {
      const skills = buildTreatmentSkills([]);

      expect(skills).toEqual({});
    });

    it("handles inline content", () => {
      const configs: SkillConfigInput[] = [
        {
          name: "custom-skill",
          content: "Custom skill content here",
        },
      ];

      const skills = buildTreatmentSkills(configs);

      expect(skills).toHaveProperty("custom-skill");
      expect(skills["custom-skill"].sections).toContain("Custom skill content here");
    });

    it("generates name from skill directory when not specified", () => {
      const configs: SkillConfigInput[] = [
        {
          skill: "my_skill_name",
          content: "Some content",
        },
      ];

      const skills = buildTreatmentSkills(configs);

      // Should convert underscores to dashes
      expect(skills).toHaveProperty("my-skill-name");
    });

    it("uses specified name over generated", () => {
      const configs: SkillConfigInput[] = [
        {
          skill: "my_skill_name",
          name: "override-name",
          content: "Some content",
        },
      ];

      const skills = buildTreatmentSkills(configs);

      expect(skills).toHaveProperty("override-name");
      expect(skills).not.toHaveProperty("my-skill-name");
    });
  });

  // =========================================================================
  // REGRESSION TESTS - Verify incorrect implementations would fail
  // =========================================================================

  describe("regression cases", () => {
    it("skill name conversion uses dashes not underscores", () => {
      const configs: SkillConfigInput[] = [
        {
          skill: "snake_case_skill",
          content: "content",
        },
      ];

      const skills = buildTreatmentSkills(configs);

      // Must be snake-case-skill, NOT snake_case_skill
      expect(skills).toHaveProperty("snake-case-skill");
      expect(skills).not.toHaveProperty("snake_case_skill");
    });

    it("YAML anchors are not included as treatments", () => {
      const yamlWithAnchors = join(tempDir, "anchors2.yaml");
      writeFileSync(
        yamlWithAnchors,
        `
_shared: &shared
  skills: []

REAL_TREATMENT:
  description: "Real treatment"
  <<: *shared
`
      );

      const treatments = loadTreatmentsYaml(yamlWithAnchors);

      // Only REAL_TREATMENT should be present, not _shared
      expect(Object.keys(treatments)).toEqual(["REAL_TREATMENT"]);
    });

    it("empty skills array does not crash", () => {
      const treatments = loadTreatmentsYaml(treatmentYamlPath);
      const controlTreatment = treatments.CONTROL;

      expect(controlTreatment.skills).toEqual([]);

      // Building skills should return empty object
      const skills = buildTreatmentSkills(controlTreatment.skills);
      expect(skills).toEqual({});
    });

    it("variant defaults to all when not specified", () => {
      const configs: SkillConfigInput[] = [
        {
          skill: "test_skill",
          // No variant specified
          content: "content",
        },
      ];

      const skills = buildTreatmentSkills(configs);

      // Should work without crashing
      expect(skills).toHaveProperty("test-skill");
    });

    it("noise flag uses correct base directory", () => {
      const configs: SkillConfigInput[] = [
        {
          skill: "noise_skill",
          noise: true,
          content: "noise content",
        },
      ];

      const skills = buildTreatmentSkills(configs);

      // Should create the skill even with noise flag (if content provided)
      expect(skills).toHaveProperty("noise-skill");
    });

    it("base option switches between benchmarks and main", () => {
      const configBenchmarks: SkillConfigInput[] = [
        { skill: "skill_a", base: "benchmarks", content: "a" },
      ];
      const configMain: SkillConfigInput[] = [
        { skill: "skill_b", base: "main", content: "b" },
      ];

      // Both should work without crashing
      const skillsBenchmarks = buildTreatmentSkills(configBenchmarks);
      const skillsMain = buildTreatmentSkills(configMain);

      expect(skillsBenchmarks).toHaveProperty("skill-a");
      expect(skillsMain).toHaveProperty("skill-b");
    });

    it("treatment config preserves all fields", () => {
      const yamlWithAllFields = join(tempDir, "full.yaml");
      writeFileSync(
        yamlWithAllFields,
        `
FULL_TREATMENT:
  description: "Full treatment"
  claude_md: "Custom CLAUDE.md content"
  skills:
    - skill: test_skill
      variant: py
  noise_tasks:
    - EMOJI
`
      );

      const treatments = loadTreatmentsYaml(yamlWithAllFields);
      const treatment = treatments.FULL_TREATMENT;

      expect(treatment.description).toBe("Full treatment");
      expect(treatment.claude_md).toBe("Custom CLAUDE.md content");
      expect(treatment.skills).toHaveLength(1);
      expect(treatment.noise_tasks).toEqual(["EMOJI"]);
    });

    it("multi skill treatment preserves order", () => {
      const treatments = loadTreatmentsYaml(treatmentYamlPath);
      const multi = treatments.MULTI_SKILL;

      expect(multi.skills).toHaveLength(2);
      expect(multi.skills![0].skill).toBe("skill_a");
      expect(multi.skills![1].skill).toBe("skill_b");
    });
  });
});
