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

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export const TASKS_DIR = join(__dirname, "..", "..", "tasks");

// =============================================================================
// TYPES
// =============================================================================

export interface TaskConfig {
  name: string;
  description: string;
  difficulty?: string;
  template_vars?: string[];
  validator_module?: string;
}

export interface Task {
  name: string;
  path: string;
  config: TaskConfig;
  environmentDir: string | null;
  dataDir: string | null;
  renderPrompt: (vars?: Record<string, string>) => string;
}

// =============================================================================
// FUNCTIONS
// =============================================================================

/**
 * List available task names from the tasks directory.
 */
export function listTasks(): string[] {
  if (!existsSync(TASKS_DIR)) {
    return [];
  }

  return readdirSync(TASKS_DIR, { withFileTypes: true })
    .filter((dirent) => {
      if (!dirent.isDirectory()) return false;
      // Must have task.toml to be a valid task
      const tomlPath = join(TASKS_DIR, dirent.name, "task.toml");
      return existsSync(tomlPath);
    })
    .map((dirent) => dirent.name)
    .sort();
}

/**
 * Parse TOML file (basic implementation for task.toml).
 * Note: This is a simplified TOML parser that handles the task.toml format.
 */
function parseToml(content: string): TaskConfig {
  const config: Partial<TaskConfig> = {};
  const lines = content.split("\n");

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || trimmed.startsWith("[")) {
      continue;
    }

    const match = trimmed.match(/^(\w+)\s*=\s*(.+)$/);
    if (match) {
      const [, key, rawValue] = match;
      let value: string | string[] = rawValue.trim();

      // Handle quoted strings
      if (value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1);
      }
      // Handle arrays
      else if (value.startsWith("[") && value.endsWith("]")) {
        value = value
          .slice(1, -1)
          .split(",")
          .map((v) => v.trim().replace(/^"|"$/g, ""))
          .filter(Boolean);
      }

      (config as Record<string, unknown>)[key] = value;
    }
  }

  return config as TaskConfig;
}

/**
 * Load a task by name.
 */
export function loadTask(name: string): Task {
  const taskPath = join(TASKS_DIR, name);

  if (!existsSync(taskPath)) {
    throw new Error(`Task not found: ${name}`);
  }

  // Load task.toml
  const tomlPath = join(taskPath, "task.toml");
  if (!existsSync(tomlPath)) {
    throw new Error(`task.toml not found in ${name}`);
  }
  const config = parseToml(readFileSync(tomlPath, "utf8"));

  // Load instruction.md
  const instructionPath = join(taskPath, "instruction.md");
  let instruction = "";
  if (existsSync(instructionPath)) {
    instruction = readFileSync(instructionPath, "utf8");
  }

  // Check for environment and data directories
  const environmentDir = join(taskPath, "environment");
  const dataDir = join(taskPath, "data");

  return {
    name: config.name || name,
    path: taskPath,
    config,
    environmentDir: existsSync(environmentDir) ? environmentDir : null,
    dataDir: existsSync(dataDir) ? dataDir : null,
    renderPrompt: (vars = {}) => {
      let prompt = instruction;
      for (const [key, value] of Object.entries(vars)) {
        prompt = prompt.replace(new RegExp(`\\{${key}\\}`, "g"), value);
      }
      return prompt;
    },
  };
}
