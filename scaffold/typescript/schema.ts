/**
 * TypeScript schema for skill benchmarks.
 *
 * Mirrors scaffold/python/schema.py - provides NoiseTask and Treatment types.
 */

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
}

// =============================================================================
// FUNCTIONS
// =============================================================================

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
