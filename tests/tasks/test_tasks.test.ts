/**
 * Generic test runner for task + treatment combinations.
 *
 * This test file uses the task-based structure where:
 * - Tasks are self-contained directories with instruction.md, task.toml, environment/, validation/
 * - Treatments are shared across tasks in treatments/{category}/*.yaml
 * - Any treatment can be used with any task
 *
 * Usage:
 *   # Run all default task/treatment combinations
 *   pnpm vitest tests/tasks/test_tasks.test.ts
 *
 *   # Run specific task with specific treatment
 *   TASK=ls-evaluator TREATMENT=LS_BASIC_PY pnpm vitest tests/tasks/test_tasks.test.ts
 *
 *   # Run specific task with multiple treatments (comma-separated)
 *   TASK=ls-evaluator TREATMENT=LS_BASIC_PY,LS_WORKFLOW_PY pnpm vitest tests/tasks/test_tasks.test.ts
 *
 *   # Run with wildcard pattern (matches all treatments starting with prefix)
 *   TASK=ls-evaluator TREATMENT=LS_BASIC_* pnpm vitest tests/tasks/test_tasks.test.ts
 *
 *   # Run with parallelism
 *   pnpm vitest tests/tasks/test_tasks.test.ts --pool=threads --poolOptions.threads.maxThreads=4
 *
 *   # Filter with pattern matching
 *   pnpm vitest tests/tasks/test_tasks.test.ts -t "ls-evaluator"
 */

import { describe, it, expect, beforeAll } from "vitest";
import { v4 as uuidv4 } from "uuid";
import { listTasks, loadTask, type Task } from "../../scaffold/typescript/tasks.js";
import {
  loadTreatments,
  buildTreatmentSkills,
  type TreatmentConfig,
} from "../../scaffold/typescript/treatments.js";

// =============================================================================
// TEST CONFIGURATION
// =============================================================================

const CLAUDE_TIMEOUT = 600_000; // 10 minutes

// Environment variable filters
const TASK_FILTER = process.env.TASK || null;
const TREATMENT_FILTER = process.env.TREATMENT || null;

// =============================================================================
// TEST GENERATION
// =============================================================================

interface TestCase {
  taskName: string;
  treatmentName: string;
}

/**
 * Expand treatment patterns into matching treatment names.
 * Supports:
 * - Exact names: "LS_BASIC_PY"
 * - Wildcards: "LS_BASIC_*" (matches LS_BASIC_PY, LS_BASIC_TS, etc.)
 * - Comma-separated: "LS_BASIC_PY,LS_WORKFLOW_PY"
 */
function expandTreatmentPatterns(
  patterns: string[],
  allTreatments: Record<string, TreatmentConfig>
): string[] {
  const treatmentNames = Object.keys(allTreatments);
  const expanded: string[] = [];

  for (const pattern of patterns) {
    if (pattern.endsWith("*")) {
      // Wildcard pattern - match prefix
      const prefix = pattern.slice(0, -1);
      const matches = treatmentNames.filter((t) => t.startsWith(prefix));
      if (matches.length === 0) {
        throw new Error(
          `No treatments match pattern: ${pattern}. Available: ${treatmentNames.join(", ")}`
        );
      }
      expanded.push(...matches);
    } else {
      // Exact match
      if (!(pattern in allTreatments)) {
        throw new Error(
          `Treatment not found: ${pattern}. Available: ${treatmentNames.join(", ")}`
        );
      }
      expanded.push(pattern);
    }
  }

  return [...new Set(expanded)]; // Deduplicate
}

function generateTestCases(): TestCase[] {
  const testCases: TestCase[] = [];
  const allTreatments = loadTreatments();
  const allTasks = listTasks();

  // Validate task filter
  if (TASK_FILTER && !allTasks.includes(TASK_FILTER)) {
    throw new Error(
      `Task not found: ${TASK_FILTER}. Available: ${allTasks.join(", ")}`
    );
  }

  // Parse and expand treatment filter (supports comma-separated and wildcards)
  let treatmentList: string[] = [];
  if (TREATMENT_FILTER) {
    const patterns = TREATMENT_FILTER.split(",").map((t) => t.trim());
    treatmentList = expandTreatmentPatterns(patterns, allTreatments);
  }

  // Determine which tasks to run
  const tasksToRun = TASK_FILTER ? [TASK_FILTER] : allTasks;

  for (const taskName of tasksToRun) {
    const task = loadTask(taskName);

    if (treatmentList.length > 0) {
      // Specific treatments requested
      for (const treatmentName of treatmentList) {
        testCases.push({ taskName, treatmentName });
      }
    } else {
      // Use default treatments for this task
      for (const treatmentName of task.defaultTreatments) {
        if (treatmentName in allTreatments) {
          testCases.push({ taskName, treatmentName });
        }
      }
    }
  }

  return testCases;
}

// =============================================================================
// TEST SUITE
// =============================================================================

describe("Task/Treatment Tests", () => {
  let allTreatments: Record<string, TreatmentConfig>;

  beforeAll(() => {
    allTreatments = loadTreatments();
  });

  const testCases = generateTestCases();

  // Skip if no test cases (e.g., task has no default_treatments)
  if (testCases.length === 0) {
    it.skip("No test cases generated", () => {});
    return;
  }

  for (const { taskName, treatmentName } of testCases) {
    it(
      `${taskName} + ${treatmentName}`,
      async () => {
        // Load task
        const task = loadTask(taskName);

        // Load treatment
        const treatmentCfg = allTreatments[treatmentName];
        if (!treatmentCfg) {
          throw new Error(`Treatment not found: ${treatmentName}`);
        }

        // Build skills
        const skills = buildTreatmentSkills(treatmentCfg.skills);

        // Generate run_id for namespace isolation
        const runId = uuidv4();

        // Build template variables
        // TODO: Read setup.template_vars from task config (Python has this)
        const templateVars: Record<string, string> = { run_id: runId };
        if (taskName === "ls-lang-evaluator") {
          templateVars.py_dataset = `bench-sql-${runId}`;
          templateVars.ts_dataset = `bench-support-${runId}`;
        }

        const prompt = task.renderPrompt(templateVars);

        // TODO: Implement actual test execution
        // This would involve:
        // 1. Setting up test context (skills, claude_md, environment)
        // 2. Running Claude with the prompt
        // 3. Parsing output and running validators
        // 4. Recording results

        // For now, just verify the setup is correct
        expect(task.name).toBe(taskName);
        expect(treatmentCfg.name).toBe(treatmentName);
        expect(prompt).toBeTruthy();
        expect(runId).toBeTruthy();

        // Log what would be tested
        console.log(`[${taskName}] + [${treatmentName}]`);
        console.log(`  Skills: ${Object.keys(skills).join(", ") || "none"}`);
        console.log(`  Run ID: ${runId}`);
      },
      CLAUDE_TIMEOUT
    );
  }
});
