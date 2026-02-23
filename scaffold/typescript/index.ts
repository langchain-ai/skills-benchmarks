/**
 * TypeScript scaffold for Claude Code skill benchmarks.
 *
 * Public API exports - mirrors scaffold/python/__init__.py.
 *
 * @example
 * import {
 *   Treatment,
 *   NoiseTask,
 *   SkillInvokedValidator,
 *   MetricsCollector,
 *   OutputQualityValidator,
 *   ExperimentLogger,
 *   parseOutput,
 *   extractEvents,
 *   runClaudeInDocker,
 *   loadTask,
 *   listTasks,
 *   loadTaskTreatments,
 * } from '@skills-benchmark/scaffold';
 */

// Schema types and functions
export {
  type NoiseTask,
  type SkillConfig,
  type Treatment,
  getFilesToRun,
  buildPrompt,
  validate,
} from "./schema.js";

// Task loading
export {
  TASKS_DIR,
  type DataHandler,
  type SetupConfig,
  type TaskConfig,
  type Task,
  listTasks,
  loadTask,
} from "./tasks.js";

// External data handlers
export {
  type HandlerArgs,
  uploadTraces,
  uploadDatasets,
  cleanupNamespace,
  runHandler,
  runTaskHandlers,
} from "./external_data_handler.js";

// Treatment loading
export {
  SKILL_BASE,
  NOISE_SKILL_BASE,
  type SkillConfigInput,
  type TreatmentConfig,
  type BuiltSkillConfig,
  loadTaskTreatments,
  getTaskTreatmentNames,
  buildNoiseTasks,
  buildTreatmentSkills,
} from "./treatments.js";

// Validation types and classes (from validation.ts - legacy class-based)
export {
  type ValidationResult,
  type Validator,
  // Class-based validators
  SkillInvokedValidator,
  TypeScriptFileValidator,
  FileValidator,
  type FileValidatorOptions,
  NoiseTaskValidator,
  MetricsCollector,
  OutputQualityValidator,
  type OutputQualityOptions,
} from "./validation.js";

// Function-based validators (from validation/ package)
export {
  type ValidatorFn,
  // Constants
  NOISE_TASK_PROMPTS,
  NOISE_TASK_DELIVERABLES,
  // Core validators
  validateFileExists,
  validatePattern,
  validateNoPattern,
  composeValidators,
  runValidators,
  validateSkillInvoked,
  getNoiseTaskPrompts,
  validateNoiseOutputs,
  // Docker validators
  validateCodeExecution,
  validatePythonExecution,
  validateTypescriptExecution,
  // Tracing validators
  validatePythonTracing,
  validateTypescriptTracing,
  validateLanguageSyntax,
} from "./validation/index.js";

// Logging types and functions
export {
  PROJECT_ROOT,
  LOGS_DIR,
  stripAnsi,
  stripNpmNoise,
  cleanOutput,
  parseOutput,
  type ParsedOutput,
  extractEvents,
  type ToolCall,
  type Events,
  type EventsSummary,
  type TreatmentResult,
  createTreatmentResult,
  hasCheck,
  hasFailedCheck,
  type ReportColumn,
  boolColumn,
  qualityColumn,
  defaultColumns,
  ExperimentLogger,
  saveEvents,
  saveRaw,
  saveReport,
  loadResultsFromReports,
} from "./logging.js";

// Utility functions
export {
  type ShellResult,
  runShell,
  checkDockerAvailable,
  checkClaudeAvailable,
  buildDockerImage,
  runInDocker,
  runNodeInDocker,
  runClaudeInDocker,
  verifyEnvironment,
  createTempDir,
  cleanupTempDir,
  writeSkill,
  writeClaudeMd,
  copyEnvironment,
  retryWithBackoff,
  readJsonFile,
  getField,
  normalizeScore,
  type EvalResult,
  evaluateWithSchema,
} from "./utils.js";
