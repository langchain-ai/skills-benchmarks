/**
 * TypeScript scaffold for Claude Code skill benchmarks.
 *
 * Public API exports - mirrors scaffold/python/__init__.py.
 *
 * @example
 * import {
 *   Treatment,
 *   NoiseTask,
 *   makeExecutionValidator,
 *   loadTask,
 *   listTasks,
 * } from '@skills-benchmark/scaffold';
 */

// Schema types and functions
export {
  type NoiseTask,
  type SkillConfig,
  type Treatment,
  buildPrompt,
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
  TREATMENTS_FOLDER,
  SKILL_BASE,
  MAIN_SKILL_BASE,
  NOISE_SKILL_BASE,
  type SkillConfigInput,
  type TreatmentConfig,
  type BuiltSkillConfig,
  loadTreatmentsYaml,
  loadTreatments,
  listTreatments,
  buildNoiseTasks,
  buildTreatmentSkills,
} from "./treatments.js";

// Validation helpers
export {
  type ValidatorFn,
  NOISE_TASK_PROMPTS,
  NOISE_TASK_DELIVERABLES,
  checkFileExists,
  checkPattern,
  checkNoPattern,
  composeValidators,
  runValidators,
  checkSkillInvoked,
  checkStarterSkillFirst,
  loadTestContext,
  getNoiseTaskPrompts,
  checkNoiseOutputs,
  checkCodeExecution,
  checkPythonExecution,
  checkTypescriptExecution,
  checkPythonTracing,
  checkTypescriptTracing,
  checkLanguageSyntax,
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
  runNodeInDocker,
  runEvalInDocker,
  makeExecutionValidator,
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
