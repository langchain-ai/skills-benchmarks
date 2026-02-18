/**
 * Treatment loader for benchmark experiments.
 *
 * Treatments are loaded from YAML configuration and built into Treatment objects
 * with fully-resolved skill configurations.
 *
 * @example
 * import { loadTaskTreatments, buildTreatmentSkills } from "./treatments.js";
 *
 * const treatments = loadTaskTreatments(taskPath);
 * const skills = buildTreatmentSkills(treatment.skills);
 */

import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";
import type { NoiseTask } from "./schema.js";
import { NOISE_TASK_PROMPTS, NOISE_TASK_DELIVERABLES } from "./validation.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export const SKILL_BASE = join(__dirname, "..", "..", "skills", "benchmarks");
export const NOISE_SKILL_BASE = join(__dirname, "..", "..", "skills", "noise");

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
 * Load treatment configurations from a task's treatments.yaml.
 */
export function loadTaskTreatments(
  taskPath: string,
): Record<string, TreatmentConfig> {
  const treatmentsPath = join(taskPath, "treatments.yaml");
  if (!existsSync(treatmentsPath)) {
    return {};
  }

  const content = readFileSync(treatmentsPath, "utf8");
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
 * Get list of treatment names defined for a task.
 */
export function getTaskTreatmentNames(taskPath: string): string[] {
  const treatments = loadTaskTreatments(taskPath);
  return Object.keys(treatments);
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
    // Note: Full skill loading would require porting skills/parser.py to TypeScript
    // For now, we just store the config for the Python side to process
    if (cfg.skill) {
      const skillDir = cfg.noise
        ? join(NOISE_SKILL_BASE, cfg.skill)
        : join(SKILL_BASE, cfg.skill);

      // Try to load skill.md content directly
      const skillMdPath = join(skillDir, "skill.md");
      const skillAllPath = join(skillDir, "skill_all.md");
      const skillPyPath = join(skillDir, "skill_py.md");
      const skillTsPath = join(skillDir, "skill_ts.md");

      let content = "";
      const variant = cfg.variant || "all";

      if (variant === "py" && existsSync(skillPyPath)) {
        content = readFileSync(skillPyPath, "utf8");
      } else if (variant === "ts" && existsSync(skillTsPath)) {
        content = readFileSync(skillTsPath, "utf8");
      } else if (existsSync(skillAllPath)) {
        content = readFileSync(skillAllPath, "utf8");
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
