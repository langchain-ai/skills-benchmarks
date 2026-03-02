/**
 * Shared test fixtures and experiment logging for Vitest.
 *
 * Mirrors tests/conftest.py - provides the same fixtures for TypeScript tests.
 *
 * Usage:
 *   import { setupTest, runClaude, recordResult } from './fixtures.js';
 *
 *   const { testDir, logger } = setupTest('my_experiment');
 *   setupTestContext(testDir, { skills: treatment.skills });
 *   const result = runClaude(testDir, prompt);
 *   const events = extractEvents(parseOutput(result.stdout));
 *   recordResult(logger, treatmentName, events, passed, failed);
 */

import {
  mkdtempSync,
  writeFileSync,
  cpSync,
  existsSync,
  readdirSync,
  copyFileSync,
  readFileSync,
  mkdirSync,
  statSync,
  unlinkSync,
} from "node:fs";
import { join, resolve, dirname } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { config as loadEnv } from "dotenv";
import { v4 as uuidv4 } from "uuid";
import { getCurrentRunTree } from "langsmith/traceable";

import {
  runClaudeInDocker,
  runNodeInDocker,
  runPythonInDocker,
  runShell,
} from "../scaffold/typescript/utils.js";
import {
  ExperimentLogger,
  parseOutput,
  extractEvents,
  saveRaw,
  saveEvents,
  saveReport,
  createTreatmentResult,
  cleanOutput,
  type Events,
} from "../scaffold/typescript/logging.js";
import type { SkillConfig } from "../scaffold/typescript/schema.js";
import {
  TEST_CONTEXT_FILE,
  TEST_RESULTS_FILE,
} from "../scaffold/typescript/validation/core.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
export const PROJECT_ROOT = resolve(__dirname, "..");

// Load .env file
loadEnv({ path: join(PROJECT_ROOT, ".env") });

// =============================================================================
// LANGSMITH PROJECT ISOLATION
// =============================================================================

let savedLangSmithProject: string | undefined;
let savedLangSmithExperiment: string | undefined;

export interface LangSmithProjectInfo {
  projectName: string;
  experimentName: string;
  /** The UUID used in bench-project-{runId} — register for cleanup. */
  runId: string;
}

/**
 * Create isolated LangSmith project for trace uploads.
 * Matches Python's langsmith_env fixture: bench-project-{uuid}.
 *
 * Returns both the project name and a stable experiment name
 * in the format "skills-benchmark:{shortid}" (like pytest).
 */
export function setupLangSmithProject(): LangSmithProjectInfo {
  const runId = uuidv4();
  const shortId = runId.slice(0, 8);
  const projectName = `bench-project-${runId}`;
  const testSuite = process.env.LANGSMITH_TEST_SUITE || "skills-benchmark";
  const experimentName = `${testSuite}:${shortId}`;

  savedLangSmithProject = process.env.LANGSMITH_PROJECT;
  savedLangSmithExperiment = process.env.LANGSMITH_EXPERIMENT;

  process.env.LANGSMITH_PROJECT = projectName;
  process.env.LANGSMITH_EXPERIMENT = testSuite;

  return { projectName, experimentName, runId };
}

/**
 * Restore original LangSmith env vars.
 */
export function cleanupLangSmithProject(): void {
  if (savedLangSmithProject !== undefined) {
    process.env.LANGSMITH_PROJECT = savedLangSmithProject;
  } else {
    delete process.env.LANGSMITH_PROJECT;
  }
  if (savedLangSmithExperiment !== undefined) {
    process.env.LANGSMITH_EXPERIMENT = savedLangSmithExperiment;
  } else {
    delete process.env.LANGSMITH_EXPERIMENT;
  }
}

// =============================================================================
// LANGSMITH TRACE CONTEXT
// =============================================================================

/**
 * Set env vars so the stop hook nests CC traces under the experiment run.
 * Matches Python's set_experiment_trace_env().
 *
 * Must be called inside a langsmith/vitest test function (traceable context).
 * Returns list of env var keys that were set (for cleanup).
 */
export function setExperimentTraceEnv(): string[] {
  try {
    const runTree = getCurrentRunTree(true); // permitAbsentRunTree = true
    if (!runTree) {
      console.log(
        "  [trace] No active run tree found — CC traces won't nest under experiment",
      );
      return [];
    }

    const keys: string[] = [];
    process.env.CC_LS_TRACE_ID = String(runTree.trace_id);
    keys.push("CC_LS_TRACE_ID");
    process.env.CC_LS_PARENT_RUN_ID = String(runTree.id);
    keys.push("CC_LS_PARENT_RUN_ID");
    process.env.CC_LS_DOTTED_ORDER = runTree.dotted_order || "";
    keys.push("CC_LS_DOTTED_ORDER");
    if (runTree.project_name) {
      process.env.CC_LANGSMITH_PROJECT = runTree.project_name;
      keys.push("CC_LANGSMITH_PROJECT");
    }
    console.log(
      `  [trace] Nesting CC traces under run ${runTree.id} (project: ${runTree.project_name})`,
    );
    return keys;
  } catch (e) {
    console.log(`  [trace] Failed to get run tree: ${e}`);
    return [];
  }
}

/**
 * Clean up trace context env vars after Claude run.
 */
export function cleanupExperimentTraceEnv(keys: string[]): void {
  for (const key of keys) {
    delete process.env[key];
  }
}

// =============================================================================
// EXPERIMENT COORDINATION (for parallel workers)
// =============================================================================

const EXPERIMENT_FILE = join(PROJECT_ROOT, ".vitest_experiment_id");

interface ExperimentCoordination {
  experimentId: string;
  createdAt: string;
}

function getOrCreateExperimentId(name: string): string {
  // Always generate a fresh ID. The coordination file exists only so
  // parallel vitest workers (if ever used) can find the same experiment.
  // We delete any stale file first to prevent leaking across runs.
  try {
    unlinkSync(EXPERIMENT_FILE);
  } catch {
    // Ignore — file may not exist
  }

  const timestamp = new Date()
    .toISOString()
    .replace(/[-:]/g, "")
    .slice(0, 15)
    .replace("T", "_");
  const experimentId = `${name}_${timestamp}`;

  writeFileSync(
    EXPERIMENT_FILE,
    JSON.stringify({
      experimentId,
      createdAt: new Date().toISOString(),
    } as ExperimentCoordination),
  );

  return experimentId;
}

// =============================================================================
// TEST SETUP
// =============================================================================

export interface TestContext {
  testDir: string;
  logger: ExperimentLogger;
}

let globalLogger: ExperimentLogger | null = null;
const runCounters: Record<string, number> = {};

/**
 * Set up test context for an experiment.
 */
export function setupTest(experimentName: string): TestContext {
  // Create temp directory
  const testDir = mkdtempSync(join(tmpdir(), "claude_test_"));

  // Get or create logger
  if (!globalLogger) {
    const experimentId = getOrCreateExperimentId(experimentName);
    globalLogger = new ExperimentLogger({
      experimentName,
      experimentId,
    });
  }

  return {
    testDir,
    logger: globalLogger,
  };
}

/**
 * Get the next repetition number for a treatment.
 */
export function getRepNumber(treatmentName: string): number {
  if (!(treatmentName in runCounters)) {
    runCounters[treatmentName] = 0;
  }
  runCounters[treatmentName]++;
  return runCounters[treatmentName];
}

// =============================================================================
// TEST CONTEXT SETUP
// =============================================================================

export interface SetupOptions {
  skills?: Record<string, SkillConfig>;
  claudeMd?: string;
  environmentDir?: string;
}

/**
 * Set up test context with skills and CLAUDE.md.
 */
export function setupTestContext(testDir: string, options: SetupOptions): void {
  const { skills, claudeMd, environmentDir } = options;

  // Write CLAUDE.md
  if (claudeMd) {
    const claudeDir = join(testDir, ".claude");
    mkdirSync(claudeDir, { recursive: true });
    writeFileSync(join(claudeDir, "CLAUDE.md"), claudeMd);
  }

  // Write skills
  if (skills) {
    for (const [skillName, skillConfig] of Object.entries(skills)) {
      if (!skillConfig) continue;

      // Support both formats:
      // 1. List of sections: {"skill-name": [section1, section2]}
      // 2. Dict with sections and scriptsDir: {sections: [...], scriptsDir: string}
      let sections: string[];
      let scriptsDir: string | undefined;

      if (Array.isArray(skillConfig)) {
        sections = skillConfig;
      } else {
        sections = skillConfig.sections;
        scriptsDir = skillConfig.scriptsDir;
      }

      if (sections && sections.length > 0) {
        const content = sections.filter((s) => s && s.trim()).join("\n\n");
        const skillDir = join(testDir, ".claude", "skills", skillName);
        mkdirSync(skillDir, { recursive: true });
        writeFileSync(join(skillDir, "SKILL.md"), content);

        // Copy scripts if provided
        if (scriptsDir && existsSync(scriptsDir)) {
          cpSync(scriptsDir, join(skillDir, "scripts"), { recursive: true });
        }
      }
    }
  }

  // Copy environment files
  if (environmentDir && existsSync(environmentDir)) {
    for (const item of readdirSync(environmentDir)) {
      const src = join(environmentDir, item);
      const dest = join(testDir, item);
      cpSync(src, dest, { recursive: true });
    }
  }

  // Set up LangSmith tracing hook if enabled (matches Python's conftest.py)
  if (process.env.TRACE_TO_LANGSMITH?.toLowerCase() === "true") {
    const project = process.env.CC_LANGSMITH_PROJECT || "claude-code-benchmark";
    runShell("setup.sh", ["setup-langsmith-hook", testDir, project], {
      check: false,
    });
  }
}

// =============================================================================
// RUN CLAUDE
// =============================================================================

export interface RunClaudeResult {
  stdout: string;
  stderr: string;
  returncode: number;
}

/**
 * Run Claude in Docker and capture output.
 */
export function runClaude(
  testDir: string,
  prompt: string,
  options: {
    timeout?: number;
    model?: string;
    logger?: ExperimentLogger;
    treatmentName?: string;
  } = {},
): RunClaudeResult {
  const { timeout = 600, logger, treatmentName } = options;
  const model = options.model || process.env.BENCH_CC_MODEL || undefined;

  const result = runClaudeInDocker(testDir, prompt, { timeout, model });

  // Save raw output if we have a logger
  if (logger && treatmentName) {
    const rep = getRepNumber(treatmentName);
    saveRaw(logger.baseDir, treatmentName, rep, result.stdout, result.stderr);
  }

  return result;
}

// =============================================================================
// RECORD RESULT
// =============================================================================

/**
 * Record validation results and save artifacts.
 */
export function recordResult(
  logger: ExperimentLogger,
  treatmentName: string,
  events: Events,
  passed: string[],
  failed: string[],
  testDir: string,
  runId = "",
): void {
  const rep = runCounters[treatmentName] || 1;

  // Save events
  saveEvents(logger.baseDir, treatmentName, rep, events);

  // Save artifacts
  saveArtifacts(logger.baseDir, treatmentName, rep, testDir);

  // Save report
  const report = {
    name: treatmentName,
    rep,
    passed: failed.length === 0,
    run_id: runId,
    checks_passed: passed,
    checks_failed: failed,
    events_summary: {
      duration_seconds: events.duration_seconds,
      num_turns: events.num_turns,
      tool_calls: events.tool_calls.length,
      files_created: events.files_created,
      skills_invoked: events.skills_invoked,
    },
    timestamp: new Date().toISOString(),
  };
  saveReport(logger.baseDir, treatmentName, rep, report);

  // Add to logger
  const result = createTreatmentResult(
    treatmentName,
    passed,
    failed,
    events,
    runId,
  );
  logger.addResult(treatmentName, result);
}

/**
 * Save Claude's generated files as artifacts.
 */
function saveArtifacts(
  baseDir: string,
  treatmentName: string,
  rep: number,
  testDir: string,
): void {
  const artifactsDir = join(
    baseDir,
    "artifacts",
    `${treatmentName.toLowerCase()}_rep${rep}`,
  );
  const claudeDir = join(artifactsDir, "claude");
  const executionDir = join(artifactsDir, "execution");

  mkdirSync(claudeDir, { recursive: true });
  mkdirSync(executionDir, { recursive: true });

  // Infrastructure dirs (copied before/after Claude runs, not Claude's work)
  const excludeDirs = new Set([
    ".claude", "node_modules", "__pycache__",
    "scaffold", "validation", "data",
  ]);
  // Environment and bench-internal files
  const excludeFiles = new Set([
    "Dockerfile", "requirements.txt", "chinook.db",
    "package.json", "package-lock.json", "tsconfig.json",
    TEST_CONTEXT_FILE,
    TEST_RESULTS_FILE,
  ]);

  // Recursively copy Claude's files, excluding infrastructure
  const claudeFiles: string[] = [];
  function walkDir(dir: string, relPrefix = ""): void {
    try {
      for (const entry of readdirSync(dir, { withFileTypes: true })) {
        const relPath = relPrefix ? `${relPrefix}/${entry.name}` : entry.name;
        if (entry.isDirectory()) {
          if (!excludeDirs.has(entry.name)) {
            walkDir(join(dir, entry.name), relPath);
          }
        } else if (entry.isFile()) {
          if (entry.name.startsWith(".")) continue;
          if (excludeFiles.has(entry.name)) continue;
          try {
            const dest = join(claudeDir, relPath);
            mkdirSync(dirname(dest), { recursive: true });
            copyFileSync(join(dir, entry.name), dest);
            claudeFiles.push(join(dir, entry.name));
          } catch {
            // Skip files that can't be copied
          }
        }
      }
    } catch {
      // Skip unreadable directories
    }
  }
  walkDir(testDir);

  // Run Claude-created scripts at root level and save execution output
  for (const filePath of claudeFiles) {
    const fileName = filePath.split("/").pop()!;
    const isRoot = dirname(filePath) === testDir;
    if (!isRoot) continue;

    const ext = fileName.split(".").pop();
    if (ext === "py") {
      try {
        const [success, output] = runPythonInDocker(testDir, fileName, { timeout: 300 });
        const baseName = fileName.replace(/\.py$/, "");
        writeFileSync(join(executionDir, `${baseName}_${success ? "success" : "error"}.txt`), cleanOutput(output));
      } catch (e) {
        writeFileSync(join(executionDir, `${fileName.replace(/\.py$/, "")}_error.txt`), String(e));
      }
    } else if (ext === "ts" || ext === "js") {
      try {
        const [success, output] = runNodeInDocker(testDir, fileName, { timeout: 300 });
        const baseName = fileName.replace(/\.(ts|js)$/, "");
        writeFileSync(join(executionDir, `${baseName}_${success ? "success" : "error"}.txt`), cleanOutput(output));
      } catch (e) {
        writeFileSync(join(executionDir, `${fileName.replace(/\.(ts|js)$/, "")}_error.txt`), String(e));
      }
    }
  }
}

// =============================================================================
// FINALIZE EXPERIMENT
// =============================================================================

/**
 * Finalize experiment and generate summary.
 */
export function finalizeExperiment(): void {
  if (globalLogger && Object.keys(globalLogger.results).length > 0) {
    globalLogger.finalize();
    printSummary(globalLogger);
  }

  // Cleanup coordination file
  try {
    unlinkSync(EXPERIMENT_FILE);
  } catch {
    // Ignore if file doesn't exist
  }

  globalLogger = null;
}

/**
 * Print summary to console.
 */
function printSummary(logger: ExperimentLogger): void {
  console.log(`\n${"=".repeat(80)}`);
  console.log("  RESULTS");
  console.log(`${"=".repeat(80)}\n`);

  console.log(
    `${"Treatment".padEnd(30)} ${"Checks".padEnd(15)} ${"Turns".padEnd(8)} ${"Duration".padEnd(10)}`,
  );
  console.log("-".repeat(80));

  for (const [treatment, runs] of Object.entries(logger.results)) {
    for (const r of runs) {
      const checksPassed = r.checks_passed.length;
      const checksTotal = checksPassed + r.checks_failed.length;
      const checkPct =
        checksTotal > 0 ? ((checksPassed / checksTotal) * 100).toFixed(0) : "0";
      const checksStr = `${checksPassed}/${checksTotal} (${checkPct}%)`;
      const turns = r.events_summary.num_turns?.toString() ?? "?";
      const dur = r.events_summary.duration_seconds
        ? `${r.events_summary.duration_seconds.toFixed(0)}s`
        : "?";
      console.log(
        `${treatment.padEnd(30)} ${checksStr.padEnd(15)} ${turns.padEnd(8)} ${dur.padEnd(10)}`,
      );
    }
  }

  console.log("-".repeat(80));

  const totalPassed = Object.values(logger.results).reduce(
    (sum, runs) => sum + runs.reduce((s, r) => s + r.checks_passed.length, 0),
    0,
  );
  const totalChecks = Object.values(logger.results).reduce(
    (sum, runs) =>
      sum +
      runs.reduce(
        (s, r) => s + r.checks_passed.length + r.checks_failed.length,
        0,
      ),
    0,
  );
  if (totalChecks > 0) {
    console.log(
      `Total: ${totalPassed}/${totalChecks} checks passed (${((totalPassed / totalChecks) * 100).toFixed(1)}%)`,
    );
  }
  console.log("=".repeat(80));
}

// =============================================================================
// ENVIRONMENT VERIFICATION
// =============================================================================

import {
  checkDockerAvailable,
  checkClaudeAvailable,
} from "../scaffold/typescript/utils.js";

/**
 * Verify that Docker, Claude CLI, and API keys are available.
 */
export function verifyTestEnvironment(): {
  docker: boolean;
  claude: boolean;
  apiKeys: boolean;
} {
  const docker = checkDockerAvailable();
  const claude = checkClaudeAvailable();
  const apiKeys = !!(
    process.env.ANTHROPIC_API_KEY && process.env.OPENAI_API_KEY
  );

  console.log("\n=== Environment Verified ===");
  console.log(`  - Docker: ${docker ? "OK" : "MISSING"}`);
  console.log(`  - Claude CLI: ${claude ? "OK" : "MISSING"}`);
  console.log(`  - API Keys: ${apiKeys ? "OK" : "MISSING"}`);
  console.log("============================\n");

  return { docker, claude, apiKeys };
}

// Re-export commonly used functions
export { parseOutput, extractEvents };
