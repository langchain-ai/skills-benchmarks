/**
 * TypeScript scaffold for Claude Code skill benchmarks.
 *
 * Public API exports - mirrors scaffold/python/__init__.py.
 *
 * @example
 * import {
 *   Treatment,
 *   NoiseTask,
 *   PythonFileValidator,
 *   SkillInvokedValidator,
 *   MetricsCollector,
 *   OutputQualityValidator,
 *   ExperimentLogger,
 *   parseOutput,
 *   extractEvents,
 *   runClaudeInDocker,
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

// Validation types and classes
export {
  type ValidationResult,
  type Validator,
  SkillInvokedValidator,
  TypeScriptFileValidator,
  FileValidator,
  type FileValidatorOptions,
  NoiseTaskValidator,
  MetricsCollector,
  OutputQualityValidator,
  type OutputQualityOptions,
} from "./validation.js";

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
