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

export interface DataHandler {
  pattern: string; // Glob pattern relative to task data dir (e.g., "trace_*.jsonl")
  handler: string; // Handler name (e.g., "upload_traces")
  args?: Record<string, unknown>; // Handler-specific arguments
}

export interface SetupConfig {
  dataHandlers: DataHandler[];
  templateVars: Record<string, string>; // Format strings that can use {run_id}
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
  validators?: string[];
  setup: SetupConfig;
}

export interface Task {
  name: string;
  path: string;
  config: TaskConfig;
  environmentDir: string | null;
  dataDir: string | null;
  defaultTreatments: string[];
  setup: SetupConfig;
  renderPrompt: (vars?: Record<string, string>) => string;
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
 * Parse a TOML value (string, array, or inline table).
 */
function parseTomlValue(rawValue: string, lines: string[], startIdx: number): { value: unknown; endIdx: number } {
  let value = rawValue.trim();
  let idx = startIdx;

  // Handle quoted strings
  if (value.startsWith('"') && value.endsWith('"')) {
    return { value: value.slice(1, -1), endIdx: idx };
  }
  // Handle single-line arrays
  if (value.startsWith("[") && value.endsWith("]")) {
    const items = value
      .slice(1, -1)
      .split(",")
      .map((v) => v.trim().replace(/^"|"$/g, ""))
      .filter(Boolean);
    return { value: items, endIdx: idx };
  }
  // Handle multiline arrays
  if (value.startsWith("[") && !value.endsWith("]")) {
    const arrayItems: string[] = [];
    const firstLineContent = value.slice(1).trim();
    if (firstLineContent) {
      const items = firstLineContent.split(",").map((v) => v.trim().replace(/^"|"$/g, "")).filter(Boolean);
      arrayItems.push(...items);
    }
    idx++;
    while (idx < lines.length) {
      const arrayLine = lines[idx].trim();
      if (arrayLine.startsWith("#")) {
        idx++;
        continue;
      }
      if (arrayLine === "]" || arrayLine.endsWith("]")) {
        if (arrayLine !== "]") {
          const lastContent = arrayLine.slice(0, -1);
          const items = lastContent.split(",").map((v) => v.trim().replace(/^"|"$/g, "").replace(/,$/, "")).filter(Boolean);
          arrayItems.push(...items);
        }
        break;
      }
      const items = arrayLine.split(",").map((v) => v.trim().replace(/^"|"$/g, "").replace(/,$/, "")).filter(Boolean);
      arrayItems.push(...items);
      idx++;
    }
    return { value: arrayItems, endIdx: idx };
  }
  // Plain value
  return { value, endIdx: idx };
}

/**
 * Parse TOML file with support for nested sections like [setup.template_vars] and [[setup.data]].
 */
function parseToml(content: string): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  const lines = content.split("\n");
  let currentSection: string[] = [];

  let i = 0;
  while (i < lines.length) {
    const trimmed = lines[i].trim();

    // Skip empty lines and comments
    if (!trimmed || trimmed.startsWith("#")) {
      i++;
      continue;
    }

    // Handle array of tables: [[section.name]]
    const arrayMatch = trimmed.match(/^\[\[(.+)\]\]$/);
    if (arrayMatch) {
      currentSection = arrayMatch[1].split(".");
      // Initialize array at path if needed
      let obj = result;
      for (let j = 0; j < currentSection.length - 1; j++) {
        if (!(currentSection[j] in obj)) {
          obj[currentSection[j]] = {};
        }
        obj = obj[currentSection[j]] as Record<string, unknown>;
      }
      const lastKey = currentSection[currentSection.length - 1];
      if (!(lastKey in obj)) {
        obj[lastKey] = [];
      }
      (obj[lastKey] as unknown[]).push({});
      i++;
      continue;
    }

    // Handle section header: [section.name]
    const sectionMatch = trimmed.match(/^\[(.+)\]$/);
    if (sectionMatch) {
      currentSection = sectionMatch[1].split(".");
      // Initialize nested objects
      let obj = result;
      for (const part of currentSection) {
        if (!(part in obj)) {
          obj[part] = {};
        }
        obj = obj[part] as Record<string, unknown>;
      }
      i++;
      continue;
    }

    // Handle key = value
    const kvMatch = trimmed.match(/^([\w-]+)\s*=\s*(.*)$/);
    if (kvMatch) {
      const [, key, rawValue] = kvMatch;
      const { value, endIdx } = parseTomlValue(rawValue, lines, i);
      i = endIdx;

      // Navigate to current section
      let obj = result;
      for (let j = 0; j < currentSection.length; j++) {
        const part = currentSection[j];
        if (!(part in obj)) {
          obj[part] = {};
        }
        const next = obj[part];
        // If it's an array (from [[section]]), use the last element
        if (Array.isArray(next)) {
          obj = next[next.length - 1] as Record<string, unknown>;
        } else {
          obj = next as Record<string, unknown>;
        }
      }
      obj[key] = value;
    }
    i++;
  }

  return result;
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
    name: metadata.name as string || "",
    description: metadata.description as string || "",
    difficulty: metadata.difficulty as string,
    category: metadata.category as string,
    tags: metadata.tags as string[],
    default_treatments: metadata.default_treatments as string[],
    template_required: template.required as string[],
    environment_description: environment.description as string,
    validators: validation.validators as string[],
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
    setup: config.setup,
    renderPrompt: (vars = {}) => {
      let prompt = instruction;
      for (const [key, value] of Object.entries(vars)) {
        prompt = prompt.replace(new RegExp(`\\{${key}\\}`, "g"), value);
      }
      return prompt;
    },
  };
}
