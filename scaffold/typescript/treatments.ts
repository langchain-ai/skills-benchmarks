/**
 * Treatment loader for benchmark experiments.
 *
 * Treatments are loaded from YAML configuration and built into Treatment objects
 * with fully-resolved skill configurations.
 *
 * ## Treatment Organization
 *
 * Treatments are organized in the `treatments/` folder by category:
 * - `common/` - Shared treatments (CONTROL, ALL_MAIN_SKILLS, etc.)
 * - `langsmith/` - LS_* treatments for LangSmith tasks
 * - `langchain_concise/` - LCC_* treatments for LangChain tasks
 * - `oss_split/` - OSSS_* treatments for OSS fix tasks (granular skills)
 * - `oss_merged/` - OSSM_* treatments for OSS fix tasks (consolidated skills)
 *
 * All treatments are shared across tasks - there are no task-specific treatments.
 *
 * @example
 * import { loadTreatments, buildTreatmentSkills } from "./treatments.js";
 *
 * const treatments = loadTreatments();
 * const skills = buildTreatmentSkills(treatment.skills);
 */

import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";
import type { NoiseTask } from "./schema.js";
import { NOISE_TASK_PROMPTS, NOISE_TASK_DELIVERABLES } from "./validation.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export const TREATMENTS_FOLDER = join(__dirname, "..", "..", "treatments");
export const SKILL_BASE = join(__dirname, "..", "..", "skills", "benchmarks");
export const MAIN_SKILL_BASE = join(__dirname, "..", "..", "skills", "main");
export const NOISE_SKILL_BASE = join(__dirname, "..", "..", "skills", "noise");

// All treatment categories (all shared, no task-specific folders)
const TREATMENT_CATEGORIES = new Set([
  "common",
  "langsmith",
  "langchain_concise",
  "oss_split",
  "oss_merged",
]);

// =============================================================================
// TYPES
// =============================================================================

export interface SkillConfigInput {
  skill?: string;
  name?: string;
  variant?: "py" | "ts" | "all";
  suffix?: boolean;
  noise?: boolean;
  content?: string;
  include_related?: boolean;
  included_sections?: string[];
  extra_sections?: string[];
  section_overrides?: Record<string, string>;
  base?: "benchmarks" | "main";
}

export interface TreatmentConfig {
  name: string;
  description: string;
  claude_md?: string;
  skills?: SkillConfigInput[];
  noise_tasks?: string[];
}

export interface BuiltSkillConfig {
  sections: string[];
  scriptsDir?: string;
  scriptFilter?: string;
}

// =============================================================================
// FUNCTIONS
// =============================================================================

/**
 * Load treatment configurations from a YAML file.
 */
export function loadTreatmentsYaml(path: string): Record<string, TreatmentConfig> {
  if (!existsSync(path)) {
    return {};
  }

  const content = readFileSync(path, "utf8");
  const data = parseYaml(content) as Record<string, unknown>;

  const treatments: Record<string, TreatmentConfig> = {};
  for (const [name, cfg] of Object.entries(data)) {
    // Skip internal keys (anchors) starting with _
    if (name.startsWith("_")) continue;

    const config = cfg as Record<string, unknown>;
    treatments[name] = {
      name,
      description: (config.description as string) || "",
      claude_md: config.claude_md as string | undefined,
      skills: config.skills as SkillConfigInput[] | undefined,
      noise_tasks: config.noise_tasks as string[] | undefined,
    };
  }

  return treatments;
}

/**
 * Load all treatments from the treatments/ folder structure.
 */
export function loadTreatments(): Record<string, TreatmentConfig> {
  if (!existsSync(TREATMENTS_FOLDER)) {
    return {};
  }

  const treatments: Record<string, TreatmentConfig> = {};

  for (const category of readdirSync(TREATMENTS_FOLDER, { withFileTypes: true })) {
    if (!category.isDirectory()) continue;
    if (!TREATMENT_CATEGORIES.has(category.name)) continue;

    const categoryPath = join(TREATMENTS_FOLDER, category.name);
    for (const file of readdirSync(categoryPath)) {
      if (!file.endsWith(".yaml")) continue;

      const yamlPath = join(categoryPath, file);
      const categoryTreatments = loadTreatmentsYaml(yamlPath);
      Object.assign(treatments, categoryTreatments);
    }
  }

  return treatments;
}

/**
 * List available treatment names.
 */
export function listTreatments(): string[] {
  const treatments = loadTreatments();
  return Object.keys(treatments);
}

/**
 * Load treatments available for a task.
 *
 * Note: All treatments are now shared. This function returns all treatments
 * regardless of taskPath (kept for backward compatibility).
 */
export function loadTaskTreatments(
  taskPath: string,
): Record<string, TreatmentConfig> {
  return loadTreatments();
}

/**
 * Get list of treatment names available for a task.
 *
 * Note: All treatments are now shared. This function returns all treatments
 * regardless of taskPath (kept for backward compatibility).
 */
export function getTaskTreatmentNames(taskPath: string): string[] {
  return listTreatments();
}

/**
 * Build NoiseTask objects from task names.
 */
export function buildNoiseTasks(noiseTaskNames: string[]): NoiseTask[] {
  return noiseTaskNames
    .filter((name) => name in NOISE_TASK_PROMPTS)
    .map((name) => ({
      prompt: NOISE_TASK_PROMPTS[name],
      deliverables: [NOISE_TASK_DELIVERABLES[name] || ""],
    }));
}

/**
 * Build skill configuration from YAML skill configs.
 * Note: This is a simplified version - full skill loading requires
 * the skills/parser module which is Python-only.
 */
export function buildTreatmentSkills(
  skillConfigs: SkillConfigInput[] | undefined,
): Record<string, BuiltSkillConfig> {
  if (!skillConfigs) return {};

  const skills: Record<string, BuiltSkillConfig> = {};

  for (const cfg of skillConfigs) {
    const name = cfg.name || cfg.skill?.replace(/_/g, "-") || "unknown";

    // Option 1: Inline content
    if (cfg.content) {
      skills[name] = { sections: [cfg.content] };
      continue;
    }

    // Option 2: Load from skill directory
    if (cfg.skill) {
      const base = cfg.base || "benchmarks";
      const baseDir = base === "main" ? MAIN_SKILL_BASE : SKILL_BASE;
      const skillDir = cfg.noise
        ? join(NOISE_SKILL_BASE, cfg.skill)
        : join(baseDir, cfg.skill);

      // Try to load skill.md content directly
      const skillMdPath = join(skillDir, "skill.md");
      const skillAllPath = join(skillDir, "skill_all.md");
      const skillPyPath = join(skillDir, "skill_py.md");
      const skillTsPath = join(skillDir, "skill_ts.md");
      const skillUpperPath = join(skillDir, "SKILL.md");

      let content = "";
      const variant = cfg.variant || "all";

      if (variant === "py" && existsSync(skillPyPath)) {
        content = readFileSync(skillPyPath, "utf8");
      } else if (variant === "ts" && existsSync(skillTsPath)) {
        content = readFileSync(skillTsPath, "utf8");
      } else if (existsSync(skillAllPath)) {
        content = readFileSync(skillAllPath, "utf8");
      } else if (existsSync(skillUpperPath)) {
        content = readFileSync(skillUpperPath, "utf8");
      } else if (existsSync(skillMdPath)) {
        content = readFileSync(skillMdPath, "utf8");
      }

      if (content) {
        skills[name] = {
          sections: [content],
          scriptsDir: existsSync(join(skillDir, "scripts"))
            ? join(skillDir, "scripts")
            : undefined,
          scriptFilter: variant !== "all" ? variant : undefined,
        };
      }
    }
  }

  return skills;
}
