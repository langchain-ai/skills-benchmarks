/**
 * Skill Parser - Parse and manipulate skill.md files.
 *
 * This module provides utilities for reading, parsing, and transforming skill
 * markdown files used in the benchmarks. Skill files use XML-tagged sections
 * to organize content, with optional language-specific blocks (<python>, <typescript>).
 *
 * ## Core Concepts
 *
 * ### Skill File Structure
 * Skill files (skill.md, skill_py.md, skill_ts.md, skill_all.md) contain:
 * - YAML frontmatter (between --- delimiters)
 * - XML-tagged sections (<overview>, <ex-basic>, <fix-common-error>, etc.)
 * - Language-specific code blocks (<python>...</python>, <typescript>...</typescript>)
 *
 * ### Variants
 * Skills can have multiple variants:
 * - skill.md: Default/combined skill
 * - skill_py.md: Python-specific content
 * - skill_ts.md: TypeScript-specific content
 * - skill_all.md: All languages combined
 *
 * ## Usage Examples
 *
 * ### Load and parse a skill:
 * ```typescript
 * import { loadSkill, loadSkillVariant } from './scaffold/typescript/skill_parser';
 *
 * // Load default skill.md
 * const skill = loadSkill("skills/benchmarks/langsmith_trace");
 * console.log(skill.sections["overview"]);
 *
 * // Load Python-specific variant
 * const skillPy = loadSkillVariant("skills/benchmarks/langsmith_trace", "py");
 * ```
 *
 * ### Extract language-specific content:
 * ```typescript
 * import { loadSkillContent, stripLangTags } from './scaffold/typescript/skill_parser';
 *
 * const content = loadSkillContent("skills/benchmarks/oss_split/lc_agents/skill_all.md");
 *
 * // Get Python-only content (remove TypeScript blocks)
 * const pyOnly = stripLangTags(content, ["typescript"]);
 *
 * // Get TypeScript-only content (remove Python blocks)
 * const tsOnly = stripLangTags(content, ["python"]);
 * ```
 *
 * ### Filter specific sections by tag:
 * ```typescript
 * import { stripByTags } from './scaffold/typescript/skill_parser';
 *
 * // Remove specific gotchas or examples by their tag attribute
 * const filtered = stripByTags(content, ["gotcha-faiss", "example-advanced"]);
 * ```
 *
 * @module skill_parser
 */

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

/**
 * Parse skill.md and return sections dict keyed by tag name.
 *
 * Frontmatter is extracted using --- delimiters (no XML tag needed).
 * All other sections preserve their XML tags for delineation.
 *
 * @param skillMdPath - Path to skill.md file
 * @param keepTags - If true, preserve XML tags around content (except frontmatter)
 * @returns Dict mapping tag names to their content
 *
 * @example
 * const sections = parseSkillMd("skill.md");
 * console.log(sections["overview"]);
 * // '<overview>\nBuild RAG systems...\n</overview>'
 */
export function parseSkillMd(
  skillMdPath: string,
  keepTags: boolean = true,
): Record<string, string> {
  const content = readFileSync(skillMdPath, "utf-8");
  const sections: Record<string, string> = {};

  // Extract frontmatter using --- delimiters
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (frontmatterMatch) {
    sections["frontmatter"] = `---\n${frontmatterMatch[1].trim()}\n---`;
  }

  // Find all XML tags and their content
  const tagPattern = /<(\w+)>([\s\S]*?)<\/\1>/g;
  let match;
  while ((match = tagPattern.exec(content)) !== null) {
    const tagName = match[1];
    if (tagName === "frontmatter") continue; // Already handled above
    const tagContent = match[2].trim();

    if (keepTags) {
      sections[tagName] = `<${tagName}>\n${tagContent}\n</${tagName}>`;
    } else {
      sections[tagName] = tagContent;
    }
  }

  return sections;
}

/**
 * Parse skill.md and return sections as ordered list of [tag, content] tuples.
 * Preserves the order of sections as they appear in the file.
 *
 * @param skillMdPath - Path to skill.md file
 * @param keepTags - If true, preserve XML tags around content (except frontmatter)
 * @returns Array of [tag_name, content] tuples in document order
 *
 * @example
 * const sections = parseSkillMdOrdered("skill.md");
 * for (const [tag, content] of sections.slice(0, 3)) {
 *   console.log(`${tag}: ${content.length} chars`);
 * }
 */
export function parseSkillMdOrdered(
  skillMdPath: string,
  keepTags: boolean = true,
): Array<[string, string]> {
  const content = readFileSync(skillMdPath, "utf-8");
  const sections: Array<[string, string]> = [];

  // Extract frontmatter using --- delimiters (always first)
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (frontmatterMatch) {
    sections.push(["frontmatter", `---\n${frontmatterMatch[1].trim()}\n---`]);
  }

  // Find all XML tags and their content
  const tagPattern = /<(\w+)>([\s\S]*?)<\/\1>/g;
  let match;
  while ((match = tagPattern.exec(content)) !== null) {
    const tagName = match[1];
    if (tagName === "frontmatter") continue;
    const tagContent = match[2].trim();

    if (keepTags) {
      sections.push([tagName, `<${tagName}>\n${tagContent}\n</${tagName}>`]);
    } else {
      sections.push([tagName, tagContent]);
    }
  }

  return sections;
}

/**
 * Load full skill content from skill.md.
 *
 * Returns the raw file content. Useful for getting the complete skill
 * as a single string for filtering or transformation.
 *
 * @param skillMdPath - Path to skill.md file
 * @returns Full file content as string
 *
 * @example
 * const content = loadSkillContent("skill_all.md");
 * const pyOnly = stripLangTags(content, ["typescript"]);
 */
export function loadSkillContent(skillMdPath: string): string {
  return readFileSync(skillMdPath, "utf-8");
}

/**
 * Get ordered list of section contents.
 *
 * This is useful for building FULL_SECTIONS-style lists where you want
 * all section contents joined together.
 *
 * @param skillMdPath - Path to skill.md file
 * @param excludeTags - Optional list of tag names to exclude
 * @param keepTags - If true, preserve XML tags around content
 * @returns List of section content strings in document order
 *
 * @example
 * const sections = getSectionList("skill.md", ["frontmatter"]);
 * const fullContent = sections.join("\n\n");
 */
export function getSectionList(
  skillMdPath: string,
  excludeTags: string[] = [],
  keepTags: boolean = true,
): string[] {
  const sections = parseSkillMdOrdered(skillMdPath, keepTags);
  return sections
    .filter(([tag]) => !excludeTags.includes(tag))
    .map(([, content]) => content);
}

/**
 * Format content with XML tags for output.
 *
 * Useful when you need to reconstruct skill.md format.
 *
 * @param tag - XML tag name
 * @param content - Section content
 * @returns Formatted string with opening and closing tags
 *
 * @example
 * const formatted = formatSectionWithTags("overview", "This is the overview.");
 * // "<overview>\nThis is the overview.\n</overview>"
 */
export function formatSectionWithTags(tag: string, content: string): string {
  return `<${tag}>\n${content}\n</${tag}>`;
}

/** Loaded skill with sections and metadata */
export interface LoadedSkill {
  /** Dict mapping tag names to section content */
  sections: Record<string, string>;
  /** List of all section contents in document order */
  all: string[];
  /** Path to scripts/ subdirectory, or null if doesn't exist */
  scriptsDir: string | null;
}

/** Loaded skill variant with script filtering info */
export interface LoadedSkillVariant extends LoadedSkill {
  /** Variant name for script filtering ("py", "ts", "all", or null) */
  scriptFilter: string | null;
}

/** Skill configuration for use in treatments */
export interface SkillConfig {
  /** List of section content strings */
  sections: string[];
  /** Path to scripts directory, or null */
  scriptsDir: string | null;
  /** Script filter variant, or null */
  scriptFilter: string | null;
}

/** Script extension mapping for variant-based filtering */
export const SCRIPT_EXTENSIONS: Record<string, string[] | null> = {
  py: [".py"],
  ts: [".ts", ".js", ".mjs", ".mts"],
  all: null, // No filtering - copy all scripts
};

/**
 * Load skill from a skill directory containing skill.md.
 *
 * Provides a convenient interface for tests to load and select sections.
 *
 * @param skillDir - Path to skill directory (contains skill.md and optionally scripts/)
 * @returns Loaded skill with sections, all content, and scripts directory
 *
 * @example
 * const trace = loadSkill("skills/benchmarks/langsmith_trace");
 *
 * // Get specific sections
 * const mySections = [
 *   trace.sections["frontmatter"],
 *   trace.sections["oneliner"],
 *   trace.sections["setup"],
 * ];
 *
 * // Or get all sections
 * const fullSections = trace.all;
 */
export function loadSkill(skillDir: string): LoadedSkill {
  const skillMdPath = join(skillDir, "skill.md");
  const sections = parseSkillMd(skillMdPath);
  const all = getSectionList(skillMdPath);
  const scriptsDir = join(skillDir, "scripts");

  return {
    sections,
    all,
    scriptsDir: existsSync(scriptsDir) ? scriptsDir : null,
  };
}

/**
 * Load skill from a specific .md file variant.
 *
 * Supports loading language-specific skill files (skill_py.md, skill_ts.md)
 * or combined files (skill_all.md). The variant also determines which scripts
 * get copied during test setup.
 *
 * @param skillDir - Path to skill directory
 * @param variant - Variant name ("py", "ts", "all") or undefined for default skill.md
 * @returns Loaded skill variant with script filter info
 *
 * @example
 * // Load Python variant - will filter to .py scripts during setup
 * const tracePy = loadSkillVariant("skills/benchmarks/langsmith_trace", "py");
 *
 * // Load TypeScript variant - will filter to .ts/.js scripts during setup
 * const traceTs = loadSkillVariant("skills/benchmarks/langsmith_trace", "ts");
 *
 * // Load combined variant - will copy all scripts during setup
 * const traceAll = loadSkillVariant("skills/benchmarks/langsmith_trace", "all");
 */
export function loadSkillVariant(
  skillDir: string,
  variant?: string,
): LoadedSkillVariant {
  const skillMdPath = variant
    ? join(skillDir, `skill_${variant}.md`)
    : join(skillDir, "skill.md");

  if (!existsSync(skillMdPath)) {
    throw new Error(`Skill file not found: ${skillMdPath}`);
  }

  const sections = parseSkillMd(skillMdPath);
  const all = getSectionList(skillMdPath);
  const scriptsDir = join(skillDir, "scripts");

  return {
    sections,
    all,
    scriptsDir: existsSync(scriptsDir) ? scriptsDir : null,
    scriptFilter: variant ?? null,
  };
}

/**
 * Split one skill into multiple skill configs by section groups.
 *
 * Useful for experiments testing whether smaller, focused skills improve
 * Claude's performance vs one large skill.
 *
 * @param skill - Result from loadSkill()
 * @param splits - Dict mapping new skill names to lists of section tags to include
 * @param baseName - Optional base name for frontmatter rewrite
 * @returns Dict mapping skill names to skill configs
 *
 * @example
 * const trace = loadSkill("skills/benchmarks/langsmith_trace");
 *
 * // Split into setup + querying skills
 * const splitSkills = splitSkill(trace, {
 *   "langsmith-trace-setup": ["frontmatter", "oneliner", "setup"],
 *   "langsmith-trace-query": ["frontmatter", "oneliner", "querying_traces"],
 * }, "langsmith-trace");
 */
export function splitSkill(
  skill: LoadedSkill,
  splits: Record<string, string[]>,
  baseName?: string,
): Record<string, SkillConfig> {
  const result: Record<string, SkillConfig> = {};

  for (const [skillName, tags] of Object.entries(splits)) {
    const sections: string[] = [];
    for (const tag of tags) {
      let content = skill.sections[tag] || "";
      if (content) {
        // Optionally rewrite frontmatter name for the split skill
        if (tag === "frontmatter" && baseName && skillName !== baseName) {
          content = content.replace(`name: ${baseName}`, `name: ${skillName}`);
        }
        sections.push(content);
      }
    }
    result[skillName] = {
      sections,
      scriptsDir: skill.scriptsDir,
      scriptFilter: null,
    };
  }

  return result;
}

/**
 * Create a skill config dict for use in treatments.
 *
 * Convenience function for creating skill configs inline.
 *
 * @param sections - List of section content strings
 * @param scriptsDir - Optional path to scripts directory
 * @param scriptFilter - Optional filter for scripts ("py", "ts", "all")
 * @returns Skill config object
 *
 * @example
 * const config = skillConfig(
 *   [HEADER, SETUP, EXAMPLES],
 *   "path/to/scripts",
 *   "py"
 * );
 */
export function skillConfig(
  sections: string[],
  scriptsDir: string | null = null,
  scriptFilter: string | null = null,
): SkillConfig {
  return { sections, scriptsDir, scriptFilter };
}

/**
 * Strip language-specific XML tags from skill content.
 *
 * Removes <python> and/or <typescript> tagged sections from content.
 * Tags may have attributes like <python tag="section-name">.
 *
 * This is useful for creating language-specific versions of skill_all.md
 * files that contain both Python and TypeScript examples.
 *
 * @param content - Skill markdown content
 * @param exclude - List of languages to exclude ("python", "typescript")
 * @returns Content with specified language sections removed
 *
 * @example
 * const content = loadSkillContent("skill_all.md");
 *
 * // Remove Python examples, keep TypeScript
 * const tsOnly = stripLangTags(content, ["python"]);
 *
 * // Remove TypeScript examples, keep Python
 * const pyOnly = stripLangTags(content, ["typescript"]);
 */
export function stripLangTags(content: string, exclude?: string[]): string {
  if (!exclude || exclude.length === 0) {
    return content;
  }

  let result = content;
  for (const lang of exclude) {
    // Match tags with optional attributes: <python> or <python tag="...">
    const pattern = new RegExp(
      `<${lang}(?:\\s+[^>]*)?>[\\s\\S]*?</${lang}>`,
      "g",
    );
    result = result.replace(pattern, "");
  }

  // Clean up excessive blank lines left after removal
  result = result.replace(/\n{3,}/g, "\n\n");

  return result;
}

/**
 * Strip content blocks by their tag attribute value.
 *
 * Removes <python tag="name"> or <typescript tag="name"> blocks where
 * the tag attribute matches one of the excluded names.
 *
 * This is useful for filtering out specific examples, gotchas, or other
 * tagged content without removing all content of that language.
 *
 * @param content - Skill markdown content
 * @param exclude - List of tag attribute values to exclude
 * @returns Content with specified tagged sections removed
 *
 * @example
 * // Remove specific gotchas by tag name
 * const filtered = stripByTags(content, ["faiss-deserialize", "import-packages"]);
 *
 * // Works with any tag attribute value
 * const filtered = stripByTags(content, ["basic-setup", "advanced-config"]);
 */
export function stripByTags(content: string, exclude?: string[]): string {
  if (!exclude || exclude.length === 0) {
    return content;
  }

  let result = content;
  for (const tagName of exclude) {
    // Match <python tag="name">...</python> or <typescript tag="name">...</typescript>
    // The tag attribute value must match exactly
    const escapedTagName = tagName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(
      `<(python|typescript)\\s+tag="${escapedTagName}"[^>]*>[\\s\\S]*?</\\1>`,
      "g",
    );
    result = result.replace(pattern, "");
  }

  // Clean up excessive blank lines left after removal
  result = result.replace(/\n{3,}/g, "\n\n");

  return result;
}
