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
  keepTags: boolean = true
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
  keepTags: boolean = true
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
  keepTags: boolean = true
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

export interface SkillConfig {
  sections: string[];
  scriptsDir: string | null;
}

/**
 * Split one skill into multiple skill configs by section groups.
 */
export function splitSkill(
  skill: LoadedSkill,
  splits: Record<string, string[]>,
  baseName?: string
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
    };
  }

  return result;
}

/**
 * Create a skill config dict for use in treatments.
 */
export function skillConfig(
  sections: string[],
  scriptsDir: string | null = null
): SkillConfig {
  return { sections, scriptsDir };
}
