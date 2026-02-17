/**
 * TypeScript schema for skill benchmarks.
 *
 * Mirrors scaffold/python/schema.py - provides NoiseTask and Treatment types.
 */

import type { Validator, ValidationResult } from "./validation.js";

// =============================================================================
// TYPES
// =============================================================================

/** A distractor task with a prompt and expected deliverables. */
export interface NoiseTask {
  prompt: string;
  deliverables: string[];
}

/** Skill configuration - list of sections or object with sections and scriptsDir. */
export type SkillConfig =
  | string[]
  | { sections: string[]; scriptsDir?: string };

/** Configuration for a single experiment treatment. */
export interface Treatment {
  description: string;
  skills?: Record<string, SkillConfig>;
  claudeMd?: string;
  noiseTasks?: NoiseTask[];
  validators?: Validator[];
}

// =============================================================================
// FUNCTIONS
// =============================================================================

/** Get list of files that validators need to run. */
export function getFilesToRun(treatment: Treatment): string[] {
  const files: string[] = [];
  for (const v of treatment.validators || []) {
    if (
      "filename" in v &&
      ("taskDescription" in v || (v as { runFile?: boolean }).runFile)
    ) {
      files.push((v as { filename: string }).filename);
    }
  }
  return [...new Set(files)];
}

/** Build experiment prompt, inserting noise tasks if present. */
export function buildPrompt(
  treatment: Treatment,
  basePrompt: string,
  task2Prompt?: string,
): string {
  const noiseTasks = treatment.noiseTasks || [];

  if (noiseTasks.length === 0) {
    return task2Prompt
      ? `Complete these tasks in order:\n\n1. ${basePrompt}\n\n2. ${task2Prompt}`
      : basePrompt;
  }

  const parts = [`1. ${basePrompt}`];
  noiseTasks.forEach((task, i) => parts.push(`${i + 2}. ${task.prompt}`));
  if (task2Prompt) parts.push(`${parts.length + 1}. ${task2Prompt}`);

  return "Complete these tasks in order:\n\n" + parts.join("\n\n");
}

/** Run all validators and return validation result. */
export async function validate(
  treatment: Treatment,
  events: Record<string, unknown>,
  testDir: string,
  outputs?: Record<string, unknown>,
): Promise<ValidationResult> {
  const allPassed: string[] = [];
  const allFailed: string[] = [];

  // Run treatment validators
  for (const validator of treatment.validators || []) {
    const { passed, failed } = await validator.validate(
      events,
      testDir,
      outputs,
    );
    allPassed.push(...passed);
    allFailed.push(...failed);
  }

  // Validate noise task deliverables
  if (treatment.noiseTasks?.length) {
    const { NoiseTaskValidator } = await import("./validation.js");
    const expectedFiles = treatment.noiseTasks.flatMap((t) => t.deliverables);
    const { passed, failed } = new NoiseTaskValidator(expectedFiles).validate(
      events,
      testDir,
    );
    allPassed.push(...passed);
    allFailed.push(...failed);
  }

  return { passed: allPassed, failed: allFailed };
}
