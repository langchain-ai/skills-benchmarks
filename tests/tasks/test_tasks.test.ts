/**
 * Generic test runner for task + treatment combinations.
 *
 * This test file uses the task-based structure where:
 * - Tasks are self-contained directories with instruction.md, task.toml, environment/, validation/
 * - Treatments are shared across tasks in treatments/{category}/*.yaml
 * - Any treatment can be used with any task
 *
 * Usage:
 *   # Run specific task with specific treatment
 *   TASK=oss-fix-lg-persistence TREATMENT=OSSS_MIXED_20 pnpm vitest tests/tasks/test_tasks.test.ts
 *
 *   # Run specific task with multiple treatments (comma-separated)
 *   TASK=ls-evaluator TREATMENT=LS_BASIC_PY,LS_WORKFLOW_PY pnpm vitest tests/tasks/test_tasks.test.ts
 *
 *   # Run with wildcard pattern (matches all treatments starting with prefix)
 *   TASK=ls-evaluator TREATMENT=LS_BASIC_* pnpm vitest tests/tasks/test_tasks.test.ts
 *
 *   # List test cases without running (like pytest --collect-only)
 *   pnpm vitest list tests/tasks/test_tasks.test.ts
 *
 *   # Filter with pattern matching
 *   pnpm vitest tests/tasks/test_tasks.test.ts -t "ls-evaluator"
 */

import * as ls from "langsmith/vitest";
import { beforeAll, afterAll, expect } from "vitest";
import { v4 as uuidv4 } from "uuid";
import { existsSync } from "node:fs";
import { listTasks, loadTask } from "../../scaffold/typescript/tasks.js";
import {
  loadTreatments,
  buildTreatmentSkills,
  buildNoiseTasks,
  type TreatmentConfig,
} from "../../scaffold/typescript/treatments.js";
import {
  setupTest,
  setupTestContext,
  setupLangSmithProject,
  cleanupLangSmithProject,
  setExperimentTraceEnv,
  cleanupExperimentTraceEnv,
  verifyTestEnvironment,
  runClaude,
  recordResult,
  finalizeExperiment,
  parseOutput,
  extractEvents,
} from "../fixtures.js";
import {
  runTaskHandlers,
  cleanupNamespace,
} from "../../scaffold/typescript/external_data_handler.js";

// =============================================================================
// TEST CONFIGURATION
// =============================================================================

const CLAUDE_TIMEOUT = 600_000; // 10 minutes

// Environment variable filters
const TASK_FILTER = process.env.TASK || null;
const TREATMENT_FILTER = process.env.TREATMENT || null;

// Track run_ids for cleanup
const testRunIds: string[] = [];

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
  allTreatments: Record<string, TreatmentConfig>,
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
          `No treatments match pattern: ${pattern}. Available: ${treatmentNames.join(", ")}`,
        );
      }
      expanded.push(...matches);
    } else {
      // Exact match
      if (!(pattern in allTreatments)) {
        throw new Error(
          `Treatment not found: ${pattern}. Available: ${treatmentNames.join(", ")}`,
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
      `Task not found: ${TASK_FILTER}. Available: ${allTasks.join(", ")}`,
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

const testSuiteName = process.env.LANGSMITH_TEST_SUITE || "skills-benchmark";

// Create isolated LangSmith project at module level (ls.describe needs projectName
// before beforeAll runs). Env vars must also be set before ls.describe evaluates.
const langsmithInfo = setupLangSmithProject();

ls.describe(
  testSuiteName,
  () => {
    let allTreatments: Record<string, TreatmentConfig>;

    beforeAll(() => {
      allTreatments = loadTreatments();
      const env = verifyTestEnvironment();
      if (!env.docker || !env.claude || !env.apiKeys) {
        throw new Error(
          `Environment not ready: docker=${env.docker}, claude=${env.claude}, apiKeys=${env.apiKeys}`,
        );
      }
      testRunIds.push(langsmithInfo.runId);
      console.log(`\nLANGSMITH PROJECT: ${langsmithInfo.projectName}`);
      console.log(`LANGSMITH EXPERIMENT: ${langsmithInfo.experimentName}\n`);
    });

    afterAll(async () => {
      // Cleanup LangSmith resources
      for (const runId of testRunIds) {
        try {
          await cleanupNamespace({ run_id: runId });
        } catch {
          // Ignore cleanup errors
        }
      }

      // Restore LangSmith env vars
      cleanupLangSmithProject();

      // Finalize experiment
      finalizeExperiment();
    });

    const testCases = generateTestCases();

    if (testCases.length === 0) {
      return;
    }

    for (const { taskName, treatmentName } of testCases) {
      ls.test(
        `${taskName} + ${treatmentName}`,
        { inputs: { task_name: taskName, treatment_name: treatmentName } },
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
          const noiseTasks = treatmentCfg.noise_tasks
            ? buildNoiseTasks(treatmentCfg.noise_tasks)
            : [];

          // Generate run_id for namespace isolation
          const runId = uuidv4();
          testRunIds.push(runId);

          // Build template variables from task config
          const templateVars: Record<string, string> = { run_id: runId };
          for (const [key, template] of Object.entries(
            task.setup.templateVars,
          )) {
            templateVars[key] = template.replace("{run_id}", runId);
          }

          let prompt = task.renderPrompt(templateVars);

          // Add noise tasks to prompt if any
          if (noiseTasks.length > 0) {
            const noisePrompts = noiseTasks
              .map((nt) => `\n\nAdditional task:\n${nt.prompt}`)
              .join("");
            prompt = prompt + noisePrompts;
          }

          // Verify setup is correct
          expect(task.name).toBe(taskName);
          expect(treatmentCfg.name).toBe(treatmentName);
          expect(prompt).toBeTruthy();
          expect(runId).toBeTruthy();

          // Combined name matches Python's format (task-treatment)
          const fullName = `${taskName}-${treatmentName}`;

          // Setup test context
          const { testDir, logger } = setupTest("task_test");

          // Run data handlers (upload traces, datasets, etc.)
          let traceIdMap: Record<string, string> = {};
          if (task.dataDir && existsSync(task.dataDir)) {
            traceIdMap = await runTaskHandlers(
              task.setup.dataHandlers,
              task.dataDir,
              process.env.LANGSMITH_PROJECT || null,
              runId,
            );
          }

          // Setup test context with skills, claude_md, environment
          setupTestContext(testDir, {
            skills,
            claudeMd: treatmentCfg.claude_md,
            environmentDir: task.environmentDir || undefined,
          });

          console.log(`\n[${taskName}] + [${treatmentName}]`);
          console.log(`  Test dir: ${testDir}`);
          console.log(`  Run ID: ${runId}`);
          console.log(`  Skills: ${Object.keys(skills).join(", ") || "none"}`);

          // Pass experiment trace context to Docker so stop_hook nests CC traces
          // under the experiment run (visible when clicking the experiment row)
          const ccEnvKeys = setExperimentTraceEnv();

          // Run Claude
          let result: ReturnType<typeof runClaude>;
          try {
            result = runClaude(testDir, prompt, {
              timeout: 600,
              logger,
              treatmentName: fullName,
            });
          } finally {
            cleanupExperimentTraceEnv(ccEnvKeys);
          }

          // Parse output and extract events
          const parsed = parseOutput(result.stdout);
          const events = extractEvents(parsed);

          console.log(
            `  Duration: ${events.duration_seconds?.toFixed(0) || "?"}s`,
          );
          console.log(`  Turns: ${events.num_turns || "?"}`);
          console.log(
            `  Skills invoked: ${events.skills_invoked?.join(", ") || "none"}`,
          );

          // Run task validators (same as Python's test_tasks.py)
          const validators = task.loadValidators();
          const outputs: Record<string, unknown> = {
            run_id: runId,
            langsmith_env: process.env.LANGSMITH_PROJECT || null,
            treatment_name: treatmentName,
            events,
            noise_tasks: treatmentCfg.noise_tasks || [],
            trace_id_map: traceIdMap,
          };

          let passed: string[] = [];
          let failed: string[] = [];

          if (validators.length > 0) {
            for (const validator of validators) {
              const result = validator(testDir, outputs);
              passed.push(...result.passed);
              failed.push(...result.failed);
            }
          } else {
            // No validators configured — fall back to basic checks
            if (events.skills_invoked && events.skills_invoked.length > 0) {
              passed.push("skills_invoked");
            }
            if (result.returncode === 0) {
              passed.push("claude_completed");
            } else {
              failed.push("claude_failed");
            }
          }

          // Log outputs to LangSmith experiment
          ls.logOutputs({
            skills_invoked: events.skills_invoked || [],
            passed_checks: passed,
            failed_checks: failed,
          });

          // Log feedback scores to LangSmith experiment
          const totalChecks = passed.length + failed.length;
          const duration = events.duration_seconds || 0;
          const numTurns = events.num_turns || 0;

          if (duration) {
            ls.logFeedback({ key: "duration_seconds", score: duration });
          }
          if (numTurns) {
            ls.logFeedback({ key: "num_turns", score: numTurns });
          }
          if (totalChecks > 0) {
            ls.logFeedback({
              key: "checks_pass_rate",
              score: passed.length / totalChecks,
            });
          }

          // Record results (local experiment logs)
          recordResult(
            logger,
            fullName,
            events,
            passed,
            failed,
            testDir,
            runId,
          );

          // Assert no failures
          if (failed.length > 0) {
            throw new Error(`Validation failed: ${failed.join(", ")}`);
          }
        },
        CLAUDE_TIMEOUT,
      );
    }
  },
  // Pass projectName so the experiment is created in our bench-project-{uuid}
  // with a stable name like "skills-benchmark:a9e089bc" (like pytest does).
  { projectName: langsmithInfo.experimentName },
);
