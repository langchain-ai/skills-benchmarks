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
  category?: string;
  tags?: string[];
  default_treatments?: string[];
  template_vars?: string[];
  validator_module?: string;
}

export interface Task {
  name: string;
  path: string;
  config: TaskConfig;
  environmentDir: string | null;
  dataDir: string | null;
  defaultTreatments: string[];
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
 * Note: This is a simplified TOML parser that handles the task.toml format,
 * including multiline arrays.
 */
function parseToml(content: string): TaskConfig {
  const config: Partial<TaskConfig> = {};
  const lines = content.split("\n");

  let i = 0;
  while (i < lines.length) {
    const trimmed = lines[i].trim();

    // Skip empty lines, comments, and section headers
    if (!trimmed || trimmed.startsWith("#") || trimmed.startsWith("[")) {
      i++;
      continue;
    }

    const match = trimmed.match(/^(\w+)\s*=\s*(.*)$/);
    if (match) {
      const [, key, rawValue] = match;
      let value: string | string[] = rawValue.trim();

      // Handle quoted strings
      if (value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1);
      }
      // Handle single-line arrays
      else if (value.startsWith("[") && value.endsWith("]")) {
        value = value
          .slice(1, -1)
          .split(",")
          .map((v) => v.trim().replace(/^"|"$/g, ""))
          .filter(Boolean);
      }
      // Handle multiline arrays
      else if (value.startsWith("[") && !value.endsWith("]")) {
        const arrayItems: string[] = [];
        // Parse items from first line if any
        const firstLineContent = value.slice(1).trim();
        if (firstLineContent) {
          const items = firstLineContent.split(",").map((v) => v.trim().replace(/^"|"$/g, "")).filter(Boolean);
          arrayItems.push(...items);
        }
        // Continue reading lines until we find the closing bracket
        i++;
        while (i < lines.length) {
          const arrayLine = lines[i].trim();
          if (arrayLine.startsWith("#")) {
            i++;
            continue;
          }
          if (arrayLine === "]" || arrayLine.endsWith("]")) {
            // Handle last line with items before closing bracket
            if (arrayLine !== "]") {
              const lastContent = arrayLine.slice(0, -1);
              const items = lastContent.split(",").map((v) => v.trim().replace(/^"|"$/g, "").replace(/,$/, "")).filter(Boolean);
              arrayItems.push(...items);
            }
            break;
          }
          // Parse items from this line
          const items = arrayLine.split(",").map((v) => v.trim().replace(/^"|"$/g, "").replace(/,$/, "")).filter(Boolean);
          arrayItems.push(...items);
          i++;
        }
        value = arrayItems;
      }

      (config as Record<string, unknown>)[key] = value;
    }
    i++;
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
    defaultTreatments: config.default_treatments || [],
    renderPrompt: (vars = {}) => {
      let prompt = instruction;
      for (const [key, value] of Object.entries(vars)) {
        prompt = prompt.replace(new RegExp(`\\{${key}\\}`, "g"), value);
      }
      return prompt;
    },
  };
}
