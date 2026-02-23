/**
 * Unit tests for skill_parser module.
 *
 * Tests cover:
 * - Section parsing and extraction
 * - Language variant loading
 * - Tag stripping and filtering
 * - Skill configuration building
 *
 * Tests mirror Python test_skill_parser.py for parity.
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { mkdtempSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

import {
  formatSectionWithTags,
  getSectionList,
  loadSkill,
  loadSkillContent,
  loadSkillVariant,
  parseSkillMd,
  parseSkillMdOrdered,
  skillConfig,
  splitSkill,
  stripByTags,
  stripLangTags,
} from "../../../scaffold/typescript/skill_parser.js";

// =============================================================================
// FIXTURES
// =============================================================================

const BASIC_SKILL_MD = `---
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
`;

const SKILL_WITH_LANG_TAGS = `---
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
`;

const SKILL_WITH_TAG_ATTRS = `---
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
`;

describe("skill_parser", () => {
  let tempDir: string;
  let basicSkillDir: string;
  let skillWithVariants: string;
  let langSkillFile: string;
  let taggedSkillFile: string;

  beforeAll(() => {
    tempDir = mkdtempSync(join(tmpdir(), "skill_parser_test_"));

    // Create basic skill directory
    basicSkillDir = join(tempDir, "test-skill");
    mkdirSync(basicSkillDir, { recursive: true });
    writeFileSync(join(basicSkillDir, "skill.md"), BASIC_SKILL_MD);

    // Create skill with variants
    skillWithVariants = join(tempDir, "multi-skill");
    mkdirSync(skillWithVariants, { recursive: true });
    writeFileSync(join(skillWithVariants, "skill.md"), BASIC_SKILL_MD);
    writeFileSync(
      join(skillWithVariants, "skill_py.md"),
      `---
name: test-skill
description: "Python variant"
---

<overview>
Python-specific overview.
</overview>
`
    );
    writeFileSync(
      join(skillWithVariants, "skill_ts.md"),
      `---
name: test-skill
description: "TypeScript variant"
---

<overview>
TypeScript-specific overview.
</overview>
`
    );
    writeFileSync(join(skillWithVariants, "skill_all.md"), SKILL_WITH_LANG_TAGS);

    // Create scripts directory
    const scriptsDir = join(skillWithVariants, "scripts");
    mkdirSync(scriptsDir, { recursive: true });
    writeFileSync(join(scriptsDir, "example.py"), "# Python script");
    writeFileSync(join(scriptsDir, "example.ts"), "// TypeScript script");

    // Create skill files for tag tests
    langSkillFile = join(tempDir, "lang_skill.md");
    writeFileSync(langSkillFile, SKILL_WITH_LANG_TAGS);

    taggedSkillFile = join(tempDir, "tagged_skill.md");
    writeFileSync(taggedSkillFile, SKILL_WITH_TAG_ATTRS);
  });

  afterAll(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  // ===========================================================================
  // parseSkillMd TESTS
  // ===========================================================================

  describe("parseSkillMd", () => {
    it("extracts frontmatter", () => {
      const sections = parseSkillMd(join(basicSkillDir, "skill.md"));

      expect(sections).toHaveProperty("frontmatter");
      expect(sections.frontmatter).toContain("name: test-skill");
      expect(sections.frontmatter.startsWith("---")).toBe(true);
      expect(sections.frontmatter.endsWith("---")).toBe(true);
    });

    it("extracts xml sections", () => {
      const sections = parseSkillMd(join(basicSkillDir, "skill.md"));

      expect(sections).toHaveProperty("overview");
      expect(sections).toHaveProperty("setup");
      expect(sections).toHaveProperty("ex_basic");
    });

    it("preserves xml tags by default", () => {
      const sections = parseSkillMd(join(basicSkillDir, "skill.md"));

      expect(sections.overview.startsWith("<overview>")).toBe(true);
      expect(sections.overview.endsWith("</overview>")).toBe(true);
    });

    it("strips xml tags when requested", () => {
      const sections = parseSkillMd(join(basicSkillDir, "skill.md"), false);

      expect(sections.overview.startsWith("<overview>")).toBe(false);
      expect(sections.overview).toContain("This is the overview section");
    });

    it("handles multiline content", () => {
      const sections = parseSkillMd(join(basicSkillDir, "skill.md"));

      expect(sections.overview).toContain("multiple lines");
    });

    it("returns empty dict for empty file", () => {
      const emptyFile = join(tempDir, "empty.md");
      writeFileSync(emptyFile, "");

      const sections = parseSkillMd(emptyFile);
      expect(Object.keys(sections).length).toBe(0);
    });

    it("handles missing frontmatter", () => {
      const noFrontmatter = join(tempDir, "no_frontmatter.md");
      writeFileSync(noFrontmatter, "<overview>\nContent here\n</overview>");

      const sections = parseSkillMd(noFrontmatter);
      expect(sections).not.toHaveProperty("frontmatter");
      expect(sections).toHaveProperty("overview");
    });
  });

  // ===========================================================================
  // parseSkillMdOrdered TESTS
  // ===========================================================================

  describe("parseSkillMdOrdered", () => {
    it("preserves section order", () => {
      const sections = parseSkillMdOrdered(join(basicSkillDir, "skill.md"));
      const tags = sections.map(([tag]) => tag);

      expect(tags).toEqual(["frontmatter", "overview", "setup", "ex_basic"]);
    });

    it("returns tuples", () => {
      const sections = parseSkillMdOrdered(join(basicSkillDir, "skill.md"));

      expect(Array.isArray(sections)).toBe(true);
      expect(sections.every((s) => Array.isArray(s) && s.length === 2)).toBe(true);
    });
  });

  // ===========================================================================
  // getSectionList TESTS
  // ===========================================================================

  describe("getSectionList", () => {
    it("returns all sections in order", () => {
      const sections = getSectionList(join(basicSkillDir, "skill.md"));

      expect(sections.length).toBe(4); // frontmatter, overview, setup, ex_basic
      expect(sections[0]).toContain("---"); // frontmatter first
      expect(sections[1]).toContain("<overview>");
    });

    it("excludes specified tags", () => {
      const sections = getSectionList(join(basicSkillDir, "skill.md"), ["frontmatter"]);

      expect(sections.length).toBe(3);
      expect(sections.some((s) => s.includes("---") && !s.includes("<"))).toBe(false);
    });

    it("excludes multiple tags", () => {
      const sections = getSectionList(join(basicSkillDir, "skill.md"), [
        "frontmatter",
        "setup",
      ]);

      expect(sections.length).toBe(2);
      const content = sections.join("\n");
      expect(content).toContain("<overview>");
      expect(content).toContain("<ex_basic>");
      expect(content).not.toContain("<setup>");
    });
  });

  // ===========================================================================
  // loadSkill TESTS
  // ===========================================================================

  describe("loadSkill", () => {
    it("loads sections dict", () => {
      const skill = loadSkill(basicSkillDir);

      expect(skill).toHaveProperty("sections");
      expect(typeof skill.sections).toBe("object");
      expect(skill.sections).toHaveProperty("overview");
    });

    it("loads all sections list", () => {
      const skill = loadSkill(basicSkillDir);

      expect(skill).toHaveProperty("all");
      expect(Array.isArray(skill.all)).toBe(true);
      expect(skill.all.length).toBe(4);
    });

    it("detects scripts dir", () => {
      const skill = loadSkill(skillWithVariants);

      expect(skill.scriptsDir).not.toBeNull();
    });

    it("handles missing scripts dir", () => {
      const skill = loadSkill(basicSkillDir);

      expect(skill.scriptsDir).toBeNull();
    });
  });

  // ===========================================================================
  // loadSkillVariant TESTS
  // ===========================================================================

  describe("loadSkillVariant", () => {
    it("loads python variant", () => {
      const skill = loadSkillVariant(skillWithVariants, "py");

      expect(skill.sections.overview).toContain("Python-specific overview");
    });

    it("loads typescript variant", () => {
      const skill = loadSkillVariant(skillWithVariants, "ts");

      expect(skill.sections.overview).toContain("TypeScript-specific overview");
    });

    it("loads all variant", () => {
      const skill = loadSkillVariant(skillWithVariants, "all");
      const examples = skill.sections.examples || "";

      expect(examples).toContain("<python>");
      expect(examples).toContain("<typescript>");
    });

    it("loads default without variant", () => {
      const skill = loadSkillVariant(skillWithVariants);

      expect(skill.sections.overview).toContain("This is the overview section");
    });

    it("sets script filter", () => {
      const skillPy = loadSkillVariant(skillWithVariants, "py");
      const skillTs = loadSkillVariant(skillWithVariants, "ts");

      expect(skillPy.scriptFilter).toBe("py");
      expect(skillTs.scriptFilter).toBe("ts");
    });

    it("throws for missing variant", () => {
      expect(() => loadSkillVariant(basicSkillDir, "py")).toThrow();
    });
  });

  // ===========================================================================
  // stripLangTags TESTS
  // ===========================================================================

  describe("stripLangTags", () => {
    it("removes python tags", () => {
      const content = loadSkillContent(langSkillFile);
      const result = stripLangTags(content, ["python"]);

      expect(result).not.toContain("<python>");
      expect(result).not.toContain("</python>");
      expect(result).not.toContain("print(");
      // TypeScript should remain
      expect(result).toContain("<typescript>");
      expect(result).toContain("console.log");
    });

    it("removes typescript tags", () => {
      const content = loadSkillContent(langSkillFile);
      const result = stripLangTags(content, ["typescript"]);

      expect(result).not.toContain("<typescript>");
      expect(result).not.toContain("</typescript>");
      expect(result).not.toContain("console.log");
      // Python should remain
      expect(result).toContain("<python>");
      expect(result).toContain("print(");
    });

    it("removes both languages", () => {
      const content = loadSkillContent(langSkillFile);
      const result = stripLangTags(content, ["python", "typescript"]);

      expect(result).not.toContain("<python>");
      expect(result).not.toContain("<typescript>");
    });

    it("preserves content with empty exclude", () => {
      const content = loadSkillContent(langSkillFile);
      const result = stripLangTags(content, []);

      expect(result).toBe(content);
    });

    it("preserves content with undefined exclude", () => {
      const content = loadSkillContent(langSkillFile);
      const result = stripLangTags(content);

      expect(result).toBe(content);
    });

    it("cleans up blank lines", () => {
      const content = loadSkillContent(langSkillFile);
      const result = stripLangTags(content, ["python"]);

      // Should not have more than 2 consecutive newlines
      expect(result).not.toContain("\n\n\n");
    });
  });

  // ===========================================================================
  // stripByTags TESTS
  // ===========================================================================

  describe("stripByTags", () => {
    it("removes tagged python block", () => {
      const content = loadSkillContent(taggedSkillFile);
      const result = stripByTags(content, ["basic"]);

      expect(result).not.toContain("Basic Python example");
      expect(result).not.toContain("Basic TypeScript example");
      // Advanced should remain
      expect(result).toContain("Advanced Python example");
    });

    it("removes only matching tag", () => {
      const content = loadSkillContent(taggedSkillFile);
      const result = stripByTags(content, ["advanced"]);

      expect(result).not.toContain("Advanced Python example");
      // Basic should remain
      expect(result).toContain("Basic Python example");
      expect(result).toContain("Basic TypeScript example");
    });

    it("preserves untagged content", () => {
      const content = loadSkillContent(taggedSkillFile);
      const result = stripByTags(content, ["nonexistent"]);

      // All content should remain
      expect(result).toContain("Basic Python example");
      expect(result).toContain("Advanced Python example");
    });
  });

  // ===========================================================================
  // skillConfig TESTS
  // ===========================================================================

  describe("skillConfig", () => {
    it("creates config dict", () => {
      const config = skillConfig(["section1", "section2"]);

      expect(config).toHaveProperty("sections");
      expect(config.sections).toEqual(["section1", "section2"]);
      expect(config.scriptsDir).toBeNull();
      expect(config.scriptFilter).toBeNull();
    });

    it("includes scripts dir", () => {
      const config = skillConfig(["section"], "/path/to/scripts");

      expect(config.scriptsDir).toBe("/path/to/scripts");
    });

    it("includes script filter", () => {
      const config = skillConfig(["section"], null, "py");

      expect(config.scriptFilter).toBe("py");
    });
  });

  // ===========================================================================
  // splitSkill TESTS
  // ===========================================================================

  describe("splitSkill", () => {
    it("splits by section tags", () => {
      const skill = loadSkill(basicSkillDir);
      const splits = splitSkill(skill, {
        "skill-overview": ["frontmatter", "overview"],
        "skill-setup": ["frontmatter", "setup"],
      });

      expect(splits).toHaveProperty("skill-overview");
      expect(splits).toHaveProperty("skill-setup");
      expect(splits["skill-overview"].sections.length).toBe(2);
      expect(splits["skill-setup"].sections.length).toBe(2);
    });

    it("preserves scripts dir", () => {
      const skill = loadSkill(skillWithVariants);
      const splits = splitSkill(skill, { split1: ["overview"] });

      expect(splits.split1.scriptsDir).toBe(skill.scriptsDir);
    });
  });

  // ===========================================================================
  // formatSectionWithTags TESTS
  // ===========================================================================

  describe("formatSectionWithTags", () => {
    it("formats with tags", () => {
      const result = formatSectionWithTags("overview", "This is content.");

      expect(result).toBe("<overview>\nThis is content.\n</overview>");
    });

    it("handles multiline content", () => {
      const content = "Line 1\nLine 2\nLine 3";
      const result = formatSectionWithTags("test", content);

      expect(result.startsWith("<test>\n")).toBe(true);
      expect(result.endsWith("\n</test>")).toBe(true);
      expect(result).toContain("Line 1\nLine 2\nLine 3");
    });
  });

  // ===========================================================================
  // REGRESSION TESTS - Verify incorrect implementations would fail
  // ===========================================================================

  describe("regression cases", () => {
    it("frontmatter uses dashes not xml", () => {
      const skillFile = join(tempDir, "frontmatter_test.md");
      writeFileSync(
        skillFile,
        `---
name: test
---

<overview>
Content
</overview>
`
      );

      const sections = parseSkillMd(skillFile);

      // Frontmatter should start with ---
      expect(sections.frontmatter.startsWith("---")).toBe(true);
      expect(sections.frontmatter).toContain("name: test");
    });

    it("nested tags not confused", () => {
      const skillFile = join(tempDir, "nested_test.md");
      writeFileSync(
        skillFile,
        `<examples>
Here is some <code>inline code</code> text.
</examples>
`
      );

      const sections = parseSkillMd(skillFile);

      // Should parse examples section, not get confused by <code>
      expect(sections).toHaveProperty("examples");
      expect(sections.examples).toContain("<code>inline code</code>");
    });

    it("section order matters", () => {
      const skillFile = join(tempDir, "order_test.md");
      // Deliberately use non-alphabetical order to catch sorting bugs
      writeFileSync(
        skillFile,
        `<zebra>
First
</zebra>

<apple>
Second
</apple>

<mango>
Third
</mango>
`
      );

      const sections = parseSkillMdOrdered(skillFile);
      const tags = sections.map(([tag]) => tag);

      // Order must be preserved - if sorted alphabetically, would be ["apple", "mango", "zebra"]
      expect(tags).toEqual(["zebra", "apple", "mango"]);
    });

    it("strip lang handles attributes", () => {
      const skillFile = join(tempDir, "attr_test.md");
      writeFileSync(
        skillFile,
        `<examples>
<python tag="test">
Python code
</python>
</examples>
`
      );

      const content = loadSkillContent(skillFile);
      const result = stripLangTags(content, ["python"]);

      // Tag with attribute should be removed
      expect(result).not.toContain("Python code");
      expect(result).not.toContain("<python");
    });

    it("exclude list not mutated", () => {
      const content = loadSkillContent(langSkillFile);
      const exclude = ["python"];
      const original = [...exclude];

      stripLangTags(content, exclude);

      expect(exclude).toEqual(original);
    });

    it("empty sections handled", () => {
      const skillFile = join(tempDir, "empty_section.md");
      writeFileSync(
        skillFile,
        `<empty>
</empty>

<nonempty>
Has content
</nonempty>
`
      );

      const sections = parseSkillMd(skillFile);

      expect(sections).toHaveProperty("empty");
      expect(sections).toHaveProperty("nonempty");
    });

    it("special characters in content", () => {
      const skillFile = join(tempDir, "special_chars.md");
      writeFileSync(
        skillFile,
        `<code>
regex = r"\\d+\\.\\d+"
path = "C:\\Users\\test"
url = "https://example.com?foo=bar&baz=qux"
</code>
`
      );

      const sections = parseSkillMd(skillFile);

      expect(sections).toHaveProperty("code");
      expect(sections.code).toContain("\\d+");
      expect(sections.code).toContain("C:\\Users");
    });
  });
});
