/**
 * TypeScript schema for skill benchmarks.
 *
 * Mirrors scaffold/python/schema.py - provides NoiseTask and Treatment types
 * for defining experimental conditions.
 *
 * @example
 * import { Treatment, NoiseTask, PythonFileValidator } from '@skills-benchmark/scaffold';
 *
 * const TREATMENTS: Record<string, Treatment> = {
 *   BASELINE: {
 *     description: "Test with skill",
 *     skills: { "my-skill": [HEADER, EXAMPLES] },
 *     validators: [new PythonFileValidator("output.py", { required: { pattern: "desc" } })],
 *   },
 * };
 */

import { z } from "zod";
import type { Validator, ValidationResult } from "./validation.js";

// =============================================================================
// NOISE TASK
// =============================================================================

/**
 * A distractor task with a prompt and expected deliverables.
 */
export interface NoiseTask {
  prompt: string;
  deliverables: string[]; // Files this task should create
}

export const NoiseTaskSchema = z.object({
  prompt: z.string(),
  deliverables: z.array(z.string()),
});

// =============================================================================
// SKILL CONFIG
// =============================================================================

/**
 * Skill configuration - either a list of sections or an object with sections and scripts_dir.
 */
export type SkillConfig =
  | string[]
  | {
      sections: string[];
      scriptsDir?: string;
    };

// =============================================================================
// TREATMENT
// =============================================================================

/**
 * Configuration for a single experiment treatment.
 */
export interface Treatment {
  description: string;
  skills?: Record<string, SkillConfig>;
  claudeMd?: string;
  noiseTasks?: NoiseTask[];
  validators?: Validator[];
}

export const TreatmentSchema = z.object({
  description: z.string(),
  skills: z.record(z.union([z.array(z.string()), z.object({
    sections: z.array(z.string()),
    scriptsDir: z.string().optional(),
  })])).optional(),
  claudeMd: z.string().optional(),
  noiseTasks: z.array(NoiseTaskSchema).optional(),
  // validators are runtime objects, can't be validated with zod
});

/**
 * Get list of files that validators need to run.
 */
export function getFilesToRun(treatment: Treatment): string[] {
  const files: string[] = [];
  for (const v of treatment.validators || []) {
    if ("filename" in v) {
      // OutputQualityValidator or PythonFileValidator with run_file
      const validator = v as { filename: string; runFile?: boolean };
      if ("taskDescription" in v || validator.runFile) {
        files.push(validator.filename);
      }
    }
  }
  // Deduplicate while preserving order
  return [...new Set(files)];
}

/**
 * Build experiment prompt, inserting noise tasks if present.
 */
export function buildPrompt(
  treatment: Treatment,
  basePrompt: string,
  task2Prompt?: string
): string {
  const noiseTasks = treatment.noiseTasks || [];

  if (noiseTasks.length === 0) {
    if (task2Prompt) {
      return `Complete these tasks in order:\n\n1. ${basePrompt}\n\n2. ${task2Prompt}`;
    }
    return basePrompt;
  }

  const parts: string[] = [`1. ${basePrompt}`];
  for (let i = 0; i < noiseTasks.length; i++) {
    parts.push(`${i + 2}. ${noiseTasks[i].prompt}`);
  }
  if (task2Prompt) {
    parts.push(`${parts.length + 1}. ${task2Prompt}`);
  }

  return "Complete these tasks in order:\n\n" + parts.join("\n\n");
}

/**
 * Run all validators and return validation result.
 */
export async function validate(
  treatment: Treatment,
  events: Record<string, unknown>,
  testDir: string,
  outputs?: Record<string, unknown>
): Promise<ValidationResult> {
  const allPassed: string[] = [];
  const allFailed: string[] = [];

  for (const validator of treatment.validators || []) {
    const { passed, failed } = await validator.validate(events, testDir, outputs);
    allPassed.push(...passed);
    allFailed.push(...failed);
  }

  // Validate noise task deliverables
  if (treatment.noiseTasks && treatment.noiseTasks.length > 0) {
    const { NoiseTaskValidator } = await import("./validation.js");
    const expectedFiles = treatment.noiseTasks.flatMap((t) => t.deliverables);
    const noiseValidator = new NoiseTaskValidator(expectedFiles);
    const { passed, failed } = noiseValidator.validate(events, testDir);
    allPassed.push(...passed);
    allFailed.push(...failed);
  }

  return { passed: allPassed, failed: allFailed };
}
