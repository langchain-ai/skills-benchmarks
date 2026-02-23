/**
 * Unit tests for scaffold/typescript/tasks.ts module.
 *
 * Tests task loading, TOML parsing, and template rendering.
 * These tests use fixtures to verify behavior that should have parity with Python.
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { mkdtempSync, rmSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { loadTask, listTasks } from "../../scaffold/typescript/tasks.js";

// =============================================================================
// FIXTURES - Mock task data for consistent testing
// =============================================================================

const BASIC_TASK_TOML = `
[metadata]
name = "test-basic"
description = "A basic test task"
difficulty = "easy"
category = "testing"
tags = ["test", "basic"]
default_treatments = ["CONTROL", "TREATMENT_A"]

[template]
required = []

[environment]
description = "Test environment"
dockerfile = "Dockerfile"
timeout_sec = 300

[validation]
validators = ["test_validator"]
`;

const TASK_WITH_SETUP_TOML = `
[metadata]
name = "test-setup"
description = "A task with setup config"
difficulty = "medium"
category = "testing"
tags = ["test", "setup"]
default_treatments = ["CONTROL"]

[template]
required = ["dataset_name", "run_id"]

[environment]
description = "Test environment with setup"

[setup.template_vars]
dataset_name = "bench-test-{run_id}"
other_var = "static-value"

[[setup.data]]
pattern = "*_dataset.json"
handler = "upload_datasets"

[[setup.data]]
pattern = "trace_*.jsonl"
handler = "upload_traces"
`;

const BASIC_INSTRUCTION = "This is a basic task instruction.";
const SETUP_INSTRUCTION = "Dataset: {dataset_name}, Run: {run_id}";

// =============================================================================
// TEST SETUP
// =============================================================================

let mockTasksDir: string;

beforeAll(() => {
  // Create mock tasks directory
  mockTasksDir = mkdtempSync(join(tmpdir(), "test_tasks_"));

  // Create basic task
  const basicTask = join(mockTasksDir, "test-basic");
  mkdirSync(basicTask);
  writeFileSync(join(basicTask, "task.toml"), BASIC_TASK_TOML);
  writeFileSync(join(basicTask, "instruction.md"), BASIC_INSTRUCTION);

  // Create task with setup
  const setupTask = join(mockTasksDir, "test-setup");
  mkdirSync(setupTask);
  writeFileSync(join(setupTask, "task.toml"), TASK_WITH_SETUP_TOML);
  writeFileSync(join(setupTask, "instruction.md"), SETUP_INSTRUCTION);
});

afterAll(() => {
  if (mockTasksDir) {
    rmSync(mockTasksDir, { recursive: true });
  }
});

// Helper to get tasks dir for tests
const getTasksDir = () => mockTasksDir;

// =============================================================================
// TESTS
// =============================================================================

describe("listTasks", () => {
  it("returns an array", () => {
    const tasks = listTasks(getTasksDir());
    expect(Array.isArray(tasks)).toBe(true);
  });

  it("returns sorted names", () => {
    const tasks = listTasks(getTasksDir());
    const sorted = [...tasks].sort();
    expect(tasks).toEqual(sorted);
  });

  it("finds valid tasks", () => {
    const tasks = listTasks(getTasksDir());
    expect(tasks).toContain("test-basic");
    expect(tasks).toContain("test-setup");
  });

  it("ignores invalid directories", () => {
    // Create invalid task (missing instruction.md)
    const invalidDir = join(mockTasksDir, "invalid-task");
    mkdirSync(invalidDir, { recursive: true });
    writeFileSync(join(invalidDir, "task.toml"), "[metadata]\nname = 'invalid'");

    const tasks = listTasks(getTasksDir());
    expect(tasks).not.toContain("invalid-task");

    // Cleanup
    rmSync(invalidDir, { recursive: true });
  });

  it("returns empty for nonexistent directory", () => {
    const tasks = listTasks("/nonexistent/path");
    expect(tasks).toEqual([]);
  });
});

describe("loadTask", () => {
  describe("basic task loading", () => {
    it("loads a basic task with minimal config", () => {
      const task = loadTask("test-basic", getTasksDir());
      expect(task.name).toBe("test-basic");
      expect(task.config.category).toBe("testing");
      expect(task.config.difficulty).toBe("easy");
      expect(task.defaultTreatments).toContain("CONTROL");
      expect(task.defaultTreatments).toContain("TREATMENT_A");
    });

    it("loads a task with setup config", () => {
      const task = loadTask("test-setup", getTasksDir());
      expect(task.name).toBe("test-setup");

      // Check template vars
      const templateVars = task.setup.templateVars;
      expect(templateVars).toHaveProperty("dataset_name");
      expect(templateVars.dataset_name).toBe("bench-test-{run_id}");
      expect(templateVars.other_var).toBe("static-value");

      // Check data handlers
      const handlers = task.setup.dataHandlers;
      expect(handlers.length).toBe(2);
      expect(handlers[0].pattern).toBe("*_dataset.json");
      expect(handlers[0].handler).toBe("upload_datasets");
      expect(handlers[1].pattern).toBe("trace_*.jsonl");
      expect(handlers[1].handler).toBe("upload_traces");
    });

    it("throws for non-existent task", () => {
      expect(() => loadTask("nonexistent-task", getTasksDir())).toThrow("Task not found");
    });

    it("has correct path set", () => {
      const task = loadTask("test-basic", getTasksDir());
      expect(task.path).toBe(join(mockTasksDir, "test-basic"));
    });
  });
});

describe("template rendering", () => {
  it("renders prompt with no required variables", () => {
    const task = loadTask("test-basic", getTasksDir());
    const prompt = task.renderPrompt();
    expect(prompt).toBe(BASIC_INSTRUCTION);
  });

  it("renders prompt with required variables", () => {
    const task = loadTask("test-setup", getTasksDir());
    const prompt = task.renderPrompt({
      dataset_name: "bench-test-abc123",
      run_id: "abc123",
    });
    expect(prompt).toContain("bench-test-abc123");
    expect(prompt).toContain("abc123");
  });
});

describe("TaskConfig parsing", () => {
  it("parses metadata fields correctly", () => {
    const task = loadTask("test-basic", getTasksDir());
    expect(task.config.name).toBe("test-basic");
    expect(task.config.description).toBe("A basic test task");
    expect(task.config.difficulty).toBe("easy");
    expect(task.config.category).toBe("testing");
    expect(task.config.tags).toContain("test");
    expect(task.config.tags).toContain("basic");
  });

  it("parses default treatments list", () => {
    const task = loadTask("test-basic", getTasksDir());
    expect(Array.isArray(task.defaultTreatments)).toBe(true);
    expect(task.defaultTreatments.length).toBe(2);
    expect(task.defaultTreatments.every((t) => typeof t === "string")).toBe(true);
  });

  it("parses template required fields", () => {
    const task = loadTask("test-setup", getTasksDir());
    expect(task.config.template_required).toContain("dataset_name");
    expect(task.config.template_required).toContain("run_id");
  });
});

describe("SetupConfig parsing", () => {
  it("parses template vars from [setup.template_vars]", () => {
    const task = loadTask("test-setup", getTasksDir());
    const templateVars = task.setup.templateVars;

    expect(Object.keys(templateVars).length).toBe(2);
    expect(templateVars.dataset_name).toBe("bench-test-{run_id}");
    expect(templateVars.other_var).toBe("static-value");
  });

  it("allows {run_id} substitution in template vars", () => {
    const task = loadTask("test-setup", getTasksDir());
    const templateVars = task.setup.templateVars;

    const result = templateVars.dataset_name.replace("{run_id}", "xyz789");
    expect(result).toBe("bench-test-xyz789");
    expect(result).not.toContain("{run_id}");
  });

  it("parses data handlers from [[setup.data]]", () => {
    const task = loadTask("test-setup", getTasksDir());
    const handlers = task.setup.dataHandlers;

    expect(handlers.length).toBe(2);
    for (const handler of handlers) {
      expect(handler).toHaveProperty("pattern");
      expect(handler).toHaveProperty("handler");
      expect(typeof handler.pattern).toBe("string");
      expect(typeof handler.handler).toBe("string");
    }
  });

  it("has empty setup config for tasks without setup", () => {
    const task = loadTask("test-basic", getTasksDir());
    expect(task.setup.templateVars).toEqual({});
    expect(task.setup.dataHandlers).toEqual([]);
  });
});
