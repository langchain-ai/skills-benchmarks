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

import {
  runClaudeInDocker,
  runNodeInDocker,
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

const __dirname = dirname(fileURLToPath(import.meta.url));
export const PROJECT_ROOT = resolve(__dirname, "..");

// Load .env file
loadEnv({ path: join(PROJECT_ROOT, ".env") });

// =============================================================================
// EXPERIMENT COORDINATION (for parallel workers)
// =============================================================================

const EXPERIMENT_FILE = join(PROJECT_ROOT, ".vitest_experiment_id");

interface ExperimentCoordination {
  experimentId: string;
  createdAt: string;
}

function getOrCreateExperimentId(name: string): string {
  // Check if experiment file exists
  if (existsSync(EXPERIMENT_FILE)) {
    try {
      const data: ExperimentCoordination = JSON.parse(
        readFileSync(EXPERIMENT_FILE, "utf8")
      );
      return data.experimentId;
    } catch {
      // File corrupted, create new
    }
  }

  // Create new experiment ID
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
    } as ExperimentCoordination)
  );

  return experimentId;
}

// =============================================================================
// TEST SETUP
// =============================================================================

export interface TestContext {
  testDir: string;
  logger: ExperimentLogger;
  cleanup: () => void;
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
    cleanup: () => {
      // Vitest handles cleanup via tmp directory
    },
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
  } = {}
): RunClaudeResult {
  const { timeout = 600, model, logger, treatmentName } = options;

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
  runId = ""
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
  const result = createTreatmentResult(treatmentName, passed, failed, events, runId);
  logger.addResult(treatmentName, result);
}

/**
 * Save Claude's generated files as artifacts.
 */
function saveArtifacts(
  baseDir: string,
  treatmentName: string,
  rep: number,
  testDir: string
): void {
  const artifactsDir = join(
    baseDir,
    "artifacts",
    `${treatmentName.toLowerCase()}_rep${rep}`
  );
  const claudeDir = join(artifactsDir, "claude");
  const executionDir = join(artifactsDir, "execution");

  mkdirSync(claudeDir, { recursive: true });
  mkdirSync(executionDir, { recursive: true });

  // Files to exclude (environment files)
  const envFiles = new Set([
    "sql_agent.py",
    "chinook.db",
    "requirements.txt",
    "Dockerfile",
  ]);

  // Copy files Claude generated
  try {
    for (const item of readdirSync(testDir)) {
      const itemPath = join(testDir, item);
      const stat = statSync(itemPath);
      if (stat.isFile() && !envFiles.has(item) && !item.startsWith(".")) {
        try {
          copyFileSync(itemPath, join(claudeDir, item));
        } catch {
          // Skip files that can't be copied
        }
      }
    }
  } catch {
    // Skip if directory doesn't exist or can't be read
  }

  // Run TypeScript/JavaScript files and save execution output
  try {
    const scriptFiles = readdirSync(testDir).filter(
      (f: string) =>
        (f.endsWith(".ts") || f.endsWith(".js")) &&
        !envFiles.has(f)
    );

    for (const scriptFile of scriptFiles) {
      try {
        const [success, output] = runNodeInDocker(testDir, scriptFile, {
          timeout: 300,
        });
        const status = success ? "success" : "error";
        const baseName = scriptFile.replace(/\.(ts|js)$/, "");
        const outputFile = join(executionDir, `${baseName}_${status}.txt`);
        writeFileSync(outputFile, cleanOutput(output));
      } catch (e) {
        const baseName = scriptFile.replace(/\.(ts|js)$/, "");
        const errorFile = join(executionDir, `${baseName}_error.txt`);
        writeFileSync(errorFile, String(e));
      }
    }
  } catch {
    // Skip if no script files
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
    `${"Treatment".padEnd(30)} ${"Checks".padEnd(15)} ${"Turns".padEnd(8)} ${"Duration".padEnd(10)}`
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
        `${treatment.padEnd(30)} ${checksStr.padEnd(15)} ${turns.padEnd(8)} ${dur.padEnd(10)}`
      );
    }
  }

  console.log("-".repeat(80));

  const totalPassed = Object.values(logger.results).reduce(
    (sum, runs) => sum + runs.reduce((s, r) => s + r.checks_passed.length, 0),
    0
  );
  const totalChecks = Object.values(logger.results).reduce(
    (sum, runs) =>
      sum +
      runs.reduce((s, r) => s + r.checks_passed.length + r.checks_failed.length, 0),
    0
  );
  if (totalChecks > 0) {
    console.log(
      `Total: ${totalPassed}/${totalChecks} checks passed (${((totalPassed / totalChecks) * 100).toFixed(1)}%)`
    );
  }
  console.log("=".repeat(80));
}

// Re-export commonly used functions
export { parseOutput, extractEvents };
