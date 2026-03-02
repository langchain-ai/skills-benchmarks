/**
 * Validation helpers for test scripts.
 *
 * These are helper functions used by test scripts running inside Docker.
 * They are NOT standalone validators — use makeExecutionValidator to
 * wire test scripts into the benchmark infrastructure.
 *
 * Mirrors scaffold/python/validation/ package structure.
 */

// Core utilities and types
export {
  type ValidationResult,
  type ValidatorFn,
  // Constants
  TEST_CONTEXT_FILE,
  TEST_RESULTS_FILE,
  NOISE_TASK_PROMPTS,
  NOISE_TASK_DELIVERABLES,
  // Functions
  loadTestContext,
  writeTestResults,
  checkFileExists,
  checkPattern,
  checkNoPattern,
  composeValidators,
  runValidators,
  checkSkillInvoked,
  checkStarterSkillFirst,
  getNoiseTaskPrompts,
  checkNoiseOutputs,
} from "./core.js";

// Docker execution validators
export {
  checkCodeExecution,
  checkPythonExecution,
  checkTypescriptExecution,
} from "./docker.js";

// Test runner
export { TestRunner, type CheckFn } from "./runner.js";

// Tracing validators
export {
  checkPythonTracing,
  checkTypescriptTracing,
  checkLanguageSyntax,
} from "./tracing.js";
