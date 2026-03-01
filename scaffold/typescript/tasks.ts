/**
 * Task loader for self-contained benchmark tasks.
 *
 * Each task is a directory containing:
 * - instruction.md: Task prompt with {variable} placeholders
 * - task.toml: Task metadata (name, description, difficulty, template vars, validators)
 * - environment/: Docker context (Dockerfile, source code)
 * - validation/: Validator implementations
 * - data/: Test data and ground truth (optional)
 *
 * @example
 * import { loadTask, listTasks } from "./tasks.js";
 *
 * const task = loadTask("ls-evaluator");
 * const prompt = task.renderPrompt({ py_dataset: "ds-py", ts_dataset: "ds-ts", run_id: "abc123" });
 */

import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseToml } from "smol-toml";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export const TASKS_DIR = join(__dirname, "..", "..", "tasks");

// =============================================================================
// TYPES
// =============================================================================

export interface DataHandler {
  pattern: string; // Glob pattern relative to task data dir (e.g., "trace_*.jsonl")
  handler: string; // Handler name (e.g., "upload_traces")
  args?: Record<string, unknown>; // Handler-specific arguments
}

export interface SetupConfig {
  dataHandlers: DataHandler[];
  templateVars: Record<string, string>; // Format strings that can use {run_id}
}

export interface ValidationConfig {
  testScripts: string | string[];
  targetArtifacts: string | string[];
  timeout: number;
}

export interface TaskConfig {
  name: string;
  description: string;
  difficulty?: string;
  category?: string;
  tags?: string[];
  default_treatments?: string[];
  template_required?: string[];
  environment_description?: string;
  validation: ValidationConfig;
  setup: SetupConfig;
}

export interface Task {
  name: string;
  path: string;
  config: TaskConfig;
  environmentDir: string | null;
  validationDir: string;
  dataDir: string | null;
  defaultTreatments: string[];
  setup: SetupConfig;
  renderPrompt: (vars?: Record<string, string>) => string;
  loadValidators: () => Array<
    (testDir: string, outputs: Record<string, unknown>) => { passed: string[]; failed: string[] }
  >;
}

// =============================================================================
// FUNCTIONS
// =============================================================================

/**
 * List available task names from the tasks directory.
 */
export function listTasks(tasksDir?: string): string[] {
  const dir = tasksDir || TASKS_DIR;
  if (!existsSync(dir)) {
    return [];
  }

  return readdirSync(dir, { withFileTypes: true })
    .filter((dirent) => {
      if (!dirent.isDirectory()) return false;
      // Must have task.toml and instruction.md to be a valid task
      const tomlPath = join(dir, dirent.name, "task.toml");
      const instructionPath = join(dir, dirent.name, "instruction.md");
      return existsSync(tomlPath) && existsSync(instructionPath);
    })
    .map((dirent) => dirent.name)
    .sort();
}

/**
 * Convert parsed TOML to TaskConfig with proper typing.
 */
function tomlToTaskConfig(toml: Record<string, unknown>): TaskConfig {
  const metadata = (toml.metadata || {}) as Record<string, unknown>;
  const template = (toml.template || {}) as Record<string, unknown>;
  const environment = (toml.environment || {}) as Record<string, unknown>;
  const validation = (toml.validation || {}) as Record<string, unknown>;
  const setupData = (toml.setup || {}) as Record<string, unknown>;

  // Parse data handlers from [[setup.data]]
  const dataHandlers: DataHandler[] = ((setupData.data || []) as Record<string, unknown>[]).map((d) => ({
    pattern: d.pattern as string,
    handler: d.handler as string,
    args: d.args as Record<string, unknown> | undefined,
  }));

  // Parse template_vars from [setup.template_vars]
  const templateVars = (setupData.template_vars || {}) as Record<string, string>;

  return {
    name: (metadata.name as string) || "",
    description: (metadata.description as string) || "",
    difficulty: metadata.difficulty as string,
    category: metadata.category as string,
    tags: metadata.tags as string[],
    default_treatments: metadata.default_treatments as string[],
    template_required: template.required as string[],
    environment_description: environment.description as string,
    validation: {
      testScripts: (validation.test_scripts as string | string[]) || "",
      targetArtifacts: (validation.target_artifacts as string | string[]) || [],
      timeout: (validation.timeout as number) || 120,
    },
    setup: {
      dataHandlers,
      templateVars,
    },
  };
}

/**
 * Load a task by name.
 */
export function loadTask(name: string, tasksDir?: string): Task {
  const dir = tasksDir || TASKS_DIR;
  const taskPath = join(dir, name);

  if (!existsSync(taskPath)) {
    throw new Error(`Task not found: ${name}`);
  }

  // Load task.toml
  const tomlPath = join(taskPath, "task.toml");
  if (!existsSync(tomlPath)) {
    throw new Error(`task.toml not found in ${name}`);
  }
  const tomlData = parseToml(readFileSync(tomlPath, "utf8"));
  const config = tomlToTaskConfig(tomlData);

  // Load instruction.md
  const instructionPath = join(taskPath, "instruction.md");
  let instruction = "";
  if (existsSync(instructionPath)) {
    instruction = readFileSync(instructionPath, "utf8");
  }

  // Check for environment, validation, and data directories
  const environmentDir = join(taskPath, "environment");
  const validationDir = join(taskPath, "validation");
  const dataDir = join(taskPath, "data");

  return {
    name: config.name || name,
    path: taskPath,
    config,
    environmentDir: existsSync(environmentDir) ? environmentDir : null,
    validationDir,
    dataDir: existsSync(dataDir) ? dataDir : null,
    defaultTreatments: config.default_treatments || [],
    setup: config.setup,
    renderPrompt: (vars = {}) => {
      let prompt = instruction;
      for (const [key, value] of Object.entries(vars)) {
        prompt = prompt.replace(new RegExp(`\\{${key}\\}`, "g"), value);
      }
      return prompt;
    },
    loadValidators: () => {
      const vc = config.validation;
      if (!vc.testScripts) return [];
      const { makeExecutionValidator } = require("./utils.js");
      return [
        makeExecutionValidator(validationDir, vc.testScripts, vc.targetArtifacts, {
          timeout: vc.timeout,
          dataDir: existsSync(dataDir) ? dataDir : undefined,
        }),
      ];
    },
  };
}
