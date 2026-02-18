/**
 * TypeScript validation utilities for benchmark tasks.
 *
 * This package provides composable validation functions organized by domain:
 * - core: Basic utilities (file exists, pattern matching, compose)
 * - tracing: Python/TypeScript LangSmith tracing validation
 * - docker: Docker-based code execution validation
 *
 * Mirrors scaffold/python/validation/ package structure.
 *
 * @example
 * import {
 *   validatePythonTracing,
 *   validateTypescriptTracing,
 *   validateCodeExecution,
 *   NOISE_TASK_PROMPTS,
 * } from "./validation/index.js";
 */

// Core utilities and types
export {
  type ValidationResult,
  type ValidatorFn,
  // Constants
  NOISE_TASK_PROMPTS,
  NOISE_TASK_DELIVERABLES,
  // Functions
  validateFileExists,
  validatePattern,
  validateNoPattern,
  composeValidators,
  runValidators,
  validateSkillInvoked,
  getNoiseTaskPrompts,
  validateNoiseOutputs,
} from "./core.js";

// Docker execution validators
export {
  validateCodeExecution,
  validatePythonExecution,
  validateTypescriptExecution,
} from "./docker.js";

// Tracing validators
export {
  validatePythonTracing,
  validateTypescriptTracing,
  validateLanguageSyntax,
} from "./tracing.js";
