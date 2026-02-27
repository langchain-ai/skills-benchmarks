/**
 * Core validation utilities.
 *
 * Basic utilities for file and pattern validation that can be composed together.
 * Mirrors scaffold/python/validation/core.py.
 */

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

// =============================================================================
// TYPES
// =============================================================================

export interface ValidationResult {
  passed: string[];
  failed: string[];
}

export type ValidatorFn = (
  testDir: string,
  outputs: Record<string, unknown>,
) => ValidationResult | Promise<ValidationResult>;

// =============================================================================
// NOISE TASK CONSTANTS
// =============================================================================

/** Noise task prompts by task name. */
export const NOISE_TASK_PROMPTS: Record<string, string> = {
  docker_patterns:
    "Create a Dockerfile for a Node.js application with multi-stage build, non-root user, and health check. Save to Dockerfile.nodejs.",
  react_components:
    "Create a React component that fetches and displays user data using hooks (useState, useEffect), with loading/error states in TypeScript. Save to UserProfile.tsx.",
  api_docs:
    "Create an OpenAPI spec for a simple user API with GET /users, POST /users, proper schemas, and error responses. Save to openapi.yaml.",
};

/** Noise task deliverable files by task name. */
export const NOISE_TASK_DELIVERABLES: Record<string, string> = {
  docker_patterns: "Dockerfile.nodejs",
  react_components: "UserProfile.tsx",
  api_docs: "openapi.yaml",
};

// =============================================================================
// HELPERS
// =============================================================================

/** Load outputs dict serialized by makeExecutionValidator. */
export function loadOutputs(path: string = "_outputs.json"): Record<string, unknown> {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch {
    return {};
  }
}

// =============================================================================
// VALIDATOR FUNCTIONS
// =============================================================================

/**
 * Check that a file exists.
 */
export function checkFileExists(
  testDir: string,
  filepath: string,
): ValidationResult {
  const path = join(testDir, filepath);
  if (existsSync(path)) {
    return { passed: [`File exists: ${filepath}`], failed: [] };
  }
  return { passed: [], failed: [`File missing: ${filepath}`] };
}

/**
 * Check that a file contains a pattern.
 */
export function checkPattern(
  filepath: string,
  pattern: string | RegExp,
  description: string,
): ValidationResult {
  if (!existsSync(filepath)) {
    return {
      passed: [],
      failed: [`${description}: file not found (${filepath.split("/").pop()})`],
    };
  }

  const content = readFileSync(filepath, "utf8");
  const regex = typeof pattern === "string" ? new RegExp(pattern) : pattern;

  if (regex.test(content)) {
    return { passed: [description], failed: [] };
  }
  return { passed: [], failed: [`Missing: ${description}`] };
}

/**
 * Check that a file does NOT contain a pattern.
 */
export function checkNoPattern(
  filepath: string,
  pattern: string | RegExp,
  description: string,
): ValidationResult {
  if (!existsSync(filepath)) {
    return {
      passed: [],
      failed: [`${description}: file not found (${filepath.split("/").pop()})`],
    };
  }

  const content = readFileSync(filepath, "utf8");
  const regex = typeof pattern === "string" ? new RegExp(pattern) : pattern;

  if (regex.test(content)) {
    return { passed: [], failed: [`Unexpected: ${description}`] };
  }
  return { passed: [`No ${description}`], failed: [] };
}

/**
 * Compose multiple validator functions into one.
 */
export function composeValidators(
  ...validators: ValidatorFn[]
): ValidatorFn {
  return async (testDir, outputs) => {
    const allPassed: string[] = [];
    const allFailed: string[] = [];

    for (const validator of validators) {
      const { passed, failed } = await validator(testDir, outputs);
      allPassed.push(...passed);
      allFailed.push(...failed);
    }

    return { passed: allPassed, failed: allFailed };
  };
}

/**
 * Run a list of validator functions.
 */
export async function runValidators(
  validators: ValidatorFn[],
  testDir: string,
  outputs: Record<string, unknown>,
): Promise<ValidationResult> {
  const allPassed: string[] = [];
  const allFailed: string[] = [];

  for (const validator of validators) {
    const { passed, failed } = await validator(testDir, outputs);
    allPassed.push(...passed);
    allFailed.push(...failed);
  }

  return { passed: allPassed, failed: allFailed };
}

/**
 * Check if a skill was invoked during the task.
 */
export function checkSkillInvoked(
  outputs: Record<string, unknown>,
  skillName: string,
  options: { required?: boolean } = {},
): ValidationResult {
  const events = (outputs?.events as Record<string, unknown>) || {};
  const skillsInvoked = (events.skills_invoked as string[]) || [];
  const required = options.required ?? false;

  if (skillsInvoked.includes(skillName)) {
    return { passed: [`Invoked ${skillName} skill`], failed: [] };
  } else if (required) {
    return { passed: [], failed: [`Did NOT invoke ${skillName} skill`] };
  }
  return { passed: [`Note: did not invoke ${skillName}`], failed: [] };
}

/**
 * Check that a starter skill was invoked first.
 */
export function checkStarterSkillFirst(
  outputs: Record<string, unknown>,
): ValidationResult {
  const treatmentName = (outputs?.treatment_name as string) || "";
  if (treatmentName === "ALL_MAIN_SKILLS") {
    return { passed: ["Note: starter skill check skipped (ALL_MAIN_SKILLS)"], failed: [] };
  }

  const events = (outputs?.events as Record<string, unknown>) || {};
  const skillsInvoked = (events.skills_invoked as string[]) || [];

  if (skillsInvoked.length === 0) {
    return { passed: ["Note: no skills invoked"], failed: [] };
  }

  const starterSkills = new Set(["langchain-oss-primer", "framework-selection"]);
  const first = skillsInvoked[0];

  if (starterSkills.has(first)) {
    return { passed: [`Starter skill invoked first: ${first}`], failed: [] };
  }

  const invokedStarters = skillsInvoked.filter((s) => starterSkills.has(s));
  if (invokedStarters.length > 0) {
    return {
      passed: [],
      failed: [`Starter skill not invoked first: first was '${first}', starters invoked later: ${invokedStarters.join(", ")}`],
    };
  }
  return {
    passed: [],
    failed: [`Starter skill not invoked: first skill was '${first}' (expected langchain-oss-primer or framework-selection)`],
  };
}

/**
 * Get prompts for noise tasks by name.
 */
export function getNoiseTaskPrompts(noiseTaskNames: string[]): string[] {
  return noiseTaskNames
    .filter((name) => name in NOISE_TASK_PROMPTS)
    .map((name) => NOISE_TASK_PROMPTS[name]);
}

/**
 * Validate that noise task deliverables were created.
 */
export function checkNoiseOutputs(
  noiseTasks: string[],
  testDir: string = ".",
): ValidationResult {
  const passed: string[] = [];
  const failed: string[] = [];

  for (const taskName of noiseTasks) {
    const deliverable = NOISE_TASK_DELIVERABLES[taskName];
    if (!deliverable) continue;

    if (existsSync(join(testDir, deliverable))) {
      passed.push(`Noise: ${deliverable} created`);
    } else {
      failed.push(`Noise: ${deliverable} NOT created`);
    }
  }

  return { passed, failed };
}
