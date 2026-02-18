/**
 * Parser for skill.md files.
 *
 * Reads skill.md files with XML-tagged sections and extracts content.
 * TypeScript equivalent of parser.py.
 */

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

/**
 * Parse skill.md and return sections dict keyed by tag name.
 *
 * Frontmatter is extracted using --- delimiters (no XML tag needed).
 * All other sections preserve their XML tags for delineation.
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
 */
export function loadSkillContent(skillMdPath: string): string {
  return readFileSync(skillMdPath, "utf-8");
}

/**
 * Get ordered list of section contents.
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

export interface LoadedSkill {
  sections: Record<string, string>;
  all: string[];
  scriptsDir: string | null;
}

export interface LoadedSkillVariant extends LoadedSkill {
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

export interface SkillConfig {
  sections: string[];
  scriptsDir: string | null;
  scriptFilter: string | null;
}

/**
 * Split one skill into multiple skill configs by section groups.
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
 * Format content with XML tags for output.
 *
 * Useful when you need to reconstruct skill.md format.
 */
export function formatSectionWithTags(tag: string, content: string): string {
  return `<${tag}>\n${content}\n</${tag}>`;
}

/**
 * Create a skill config dict for use in treatments.
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
 * @example
 * // Remove Python examples, keep TypeScript
 * const tsOnly = stripLangTags(content, ["python"]);
 *
 * // Remove TypeScript examples, keep Python
 * const pyOnly = stripLangTags(content, ["typescript"]);
 */
export function stripLangTags(
  content: string,
  exclude?: string[],
): string {
  if (!exclude || exclude.length === 0) {
    return content;
  }

  let result = content;
  for (const lang of exclude) {
    // Match tags with optional attributes: <python> or <python tag="...">
    const pattern = new RegExp(`<${lang}(?:\\s+[^>]*)?>[\\s\\S]*?</${lang}>`, "g");
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
 * @example
 * // Remove specific gotchas by tag name
 * const filtered = stripByTags(content, ["faiss-deserialize", "import-packages"]);
 *
 * // Works with any tag attribute value
 * const filtered = stripByTags(content, ["basic-setup", "advanced-config"]);
 */
export function stripByTags(
  content: string,
  exclude?: string[],
): string {
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
