/**
 * Thin wrappers around shell scripts in scaffold/shell/.
 */

import { spawnSync, type SpawnSyncOptions } from "node:child_process";
import { copyFileSync, cpSync, existsSync, mkdirSync, readFileSync, readdirSync, statSync, unlinkSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { config as loadEnv } from "dotenv";
import { TEST_CONTEXT_FILE, TEST_RESULTS_FILE } from "./validation/core.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SHELL_DIR = resolve(__dirname, "..", "shell");
const PROJECT_ROOT = resolve(__dirname, "..", "..");

loadEnv({ path: join(PROJECT_ROOT, ".env") });

// =============================================================================
// SHELL SCRIPT RUNNER
// =============================================================================

export interface ShellResult {
  stdout: string;
  stderr: string;
  returncode: number;
}

/** Run a shell script from scaffold/shell/ with proper argument handling. */
export function runShell(
  script: string,
  args: string[] = [],
  options: { timeout?: number; check?: boolean; cwd?: string } = {},
): ShellResult {
  const { timeout, check = true, cwd } = options;
  const scriptPath = join(SHELL_DIR, script);

  const spawnOptions: SpawnSyncOptions = {
    encoding: "utf8",
    stdio: ["pipe", "pipe", "pipe"],
    timeout: timeout ? timeout * 1000 : undefined,
    cwd,
    env: process.env,
  };

  const result = spawnSync("bash", [scriptPath, ...args], spawnOptions);
  const stdout = result.stdout?.toString() || "";
  const stderr = result.stderr?.toString() || "";
  const returncode = result.status ?? 1;

  if (check && returncode !== 0) {
    throw new Error(`Shell failed: ${script} ${args.join(" ")}\n${stderr}`);
  }

  return { stdout, stderr, returncode };
}

// =============================================================================
// DOCKER (via docker.sh)
// =============================================================================

export function checkDockerAvailable(): boolean {
  try {
    return (
      runShell("docker.sh", ["check"], { check: false, timeout: 10 })
        .returncode === 0
    );
  } catch {
    return false;
  }
}

export function checkClaudeAvailable(): boolean {
  try {
    return (
      spawnSync("claude", ["--version"], { stdio: "pipe", timeout: 10000 })
        .status === 0
    );
  } catch {
    return false;
  }
}

export function buildDockerImage(
  testDir: string,
  options: { force?: boolean } = {},
): string | null {
  try {
    const args = ["build", resolve(testDir)];
    if (options.force) args.push("--force");
    const result = runShell("docker.sh", args, { timeout: 300, check: false });
    return result.returncode === 0 ? result.stdout.trim() : null;
  } catch {
    return null;
  }
}


/** Run a script in Docker. Returns [success, output]. */
function _dockerRunScript(
  mode: string,
  testDir: string,
  scriptName: string,
  options: { timeout?: number; args?: string[] } = {},
): [boolean, string] {
  if (!checkDockerAvailable()) return [false, "Docker not available"];
  const { timeout = 120, args = [] } = options;
  try {
    const result = runShell(
      "docker.sh",
      [mode, resolve(testDir), scriptName, ...args],
      { timeout, check: false },
    );
    return [result.returncode === 0, result.stdout + result.stderr];
  } catch (error) {
    return [
      false,
      (error as Error).message?.includes("ETIMEDOUT")
        ? `Timeout (${timeout}s)`
        : String(error),
    ];
  }
}

/** Run Python script in Docker. Returns [success, output]. */
export function runPythonInDocker(
  testDir: string,
  scriptName: string,
  options: { timeout?: number; args?: string[] } = {},
): [boolean, string] {
  return _dockerRunScript("run-python", testDir, scriptName, options);
}

/** Run Node/TypeScript script in Docker. Returns [success, output]. */
export function runNodeInDocker(
  testDir: string,
  scriptName: string,
  options: { timeout?: number; args?: string[] } = {},
): [boolean, string] {
  return _dockerRunScript("run-node", testDir, scriptName, options);
}

/** Run script in Docker based on file extension. Returns [success, output]. */
export function runScriptInDocker(
  testDir: string,
  scriptName: string,
  options: { timeout?: number; args?: string[] } = {},
): [boolean, string] {
  if (scriptName.endsWith(".py")) return runPythonInDocker(testDir, scriptName, options);
  if (scriptName.endsWith(".ts") || scriptName.endsWith(".js")) return runNodeInDocker(testDir, scriptName, options);
  return [false, `Unsupported file type: ${scriptName}`];
}

/** Copy scaffold into testDir so test scripts can import helpers.
 *
 * Copies both Python and TypeScript scaffolds — test scripts may be
 * in either language regardless of which test runner invokes them.
 */
function copyScaffoldToDocker(testDir: string): void {
  const scaffoldRoot = resolve(__dirname, "..");

  // TypeScript scaffold
  const tsDest = join(testDir, "scaffold", "typescript");
  mkdirSync(tsDest, { recursive: true });
  copyFileSync(join(scaffoldRoot, "typescript", "utils.ts"), join(tsDest, "utils.ts"));
  const tsValidation = join(scaffoldRoot, "typescript", "validation");
  if (existsSync(tsValidation)) {
    cpSync(tsValidation, join(tsDest, "validation"), { recursive: true });
  }

  // Python scaffold (test scripts import from scaffold.python)
  const pyDest = join(testDir, "scaffold", "python");
  mkdirSync(pyDest, { recursive: true });
  writeFileSync(join(testDir, "scaffold", "__init__.py"), "");
  writeFileSync(join(pyDest, "__init__.py"), "");
  copyFileSync(join(scaffoldRoot, "python", "utils.py"), join(pyDest, "utils.py"));
  const pyValidation = join(scaffoldRoot, "python", "validation");
  if (existsSync(pyValidation)) {
    cpSync(pyValidation, join(pyDest, "validation"), { recursive: true });
  }
}

/** Copy validation/data/scaffold into testDir subdirs, run test script in Docker, return parsed JSON.
 *
 * Copies into testDir (mirroring the local task directory structure):
 * - validation/ — test scripts and helpers
 * - data/ — ground truth, test cases, reference files
 * - scaffold/typescript/ — so test scripts can import helpers
 */
export function runEvalInDocker(
  testDir: string,
  validationDir: string,
  testScript: string,
  options: { timeout?: number; dataDir?: string } = {},
): Record<string, unknown> {
  const { timeout = 120, dataDir } = options;
  const resolvedTestDir = resolve(testDir);

  // Copy validation scripts to validation/ subdir
  const valDest = join(resolvedTestDir, "validation");
  mkdirSync(valDest, { recursive: true });
  if (existsSync(validationDir)) {
    for (const entry of readdirSync(validationDir)) {
      const src = join(validationDir, entry);
      if (statSync(src).isFile()) {
        copyFileSync(src, join(valDest, entry));
      }
    }
  }

  // Copy data files to data/ subdir
  if (dataDir && existsSync(dataDir)) {
    const dataDest = join(resolvedTestDir, "data");
    mkdirSync(dataDest, { recursive: true });
    for (const entry of readdirSync(dataDir)) {
      const src = join(dataDir, entry);
      if (statSync(src).isFile()) {
        copyFileSync(src, join(dataDest, entry));
      }
    }
  }

  copyScaffoldToDocker(resolvedTestDir);

  // Remove stale results file
  const resultsPath = join(resolvedTestDir, TEST_RESULTS_FILE);
  if (existsSync(resultsPath)) {
    unlinkSync(resultsPath);
  }

  const [success, output] = runScriptInDocker(testDir, `validation/${testScript}`, { timeout });

  // Primary: read results from file (immune to stdout pollution)
  if (existsSync(resultsPath)) {
    try {
      return JSON.parse(readFileSync(resultsPath, "utf8")) as Record<string, unknown>;
    } catch {
      // fall through to stdout parsing
    }
  }

  // Fallback: parse stdout JSON
  try {
    const full = JSON.parse(output.trim());
    if (full && typeof full === "object" && !Array.isArray(full)) {
      return full as Record<string, unknown>;
    }
  } catch {
    // fall through to line-by-line
  }
  const lines = output.trim().split("\n");
  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const parsed = JSON.parse(lines[i]);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        return parsed as Record<string, unknown>;
      }
    } catch {
      continue;
    }
  }
  return {
    error: `No JSON output. success=${success}, output=${output.slice(0, 300)}`,
  };
}

/**
 * Set env vars so Docker eval scripts can nest traces under the current span.
 * Mirrors Python _set_eval_trace_env(). Returns keys that were set (for cleanup).
 */
function _setEvalTraceEnv(): string[] {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { getCurrentRunTree } = require("langsmith/run_trees");
    const runTree = getCurrentRunTree();
    if (!runTree) return [];

    const headers = runTree.toHeaders();
    const setKeys: string[] = [];
    if (headers["langsmith-trace"]) {
      process.env.BENCH_EVAL_LANGSMITH_TRACE = headers["langsmith-trace"];
      setKeys.push("BENCH_EVAL_LANGSMITH_TRACE");
    }
    if (headers["baggage"]) {
      process.env.BENCH_EVAL_BAGGAGE = headers["baggage"];
      setKeys.push("BENCH_EVAL_BAGGAGE");
    }
    return setKeys;
  } catch {
    return [];
  }
}

/** Create a standard execution validator that runs test script(s) in Docker. */
export function makeExecutionValidator(
  validationDir: string,
  testScripts: string | string[],
  targetArtifacts: string | string[],
  options: { timeout?: number; dataDir?: string } = {},
): (testDir: string, outputs: Record<string, unknown>) => { passed: string[]; failed: string[] } {
  const { timeout = 120, dataDir } = options;
  const scripts = Array.isArray(testScripts) ? testScripts : [testScripts];
  const artifacts = Array.isArray(targetArtifacts) ? targetArtifacts : [targetArtifacts];

  return (testDir: string, outputs: Record<string, unknown>) => {
    const passed: string[] = [];
    const failed: string[] = [];
    for (const artifact of artifacts) {
      if (!existsSync(join(resolve(testDir), artifact))) {
        failed.push(`Artifact not found: ${artifact}`);
      }
    }
    if (failed.length > 0) return { passed, failed };
    // Serialize run context + target artifacts for test scripts
    const context = outputs ? { ...outputs, target_artifacts: artifacts } : { target_artifacts: artifacts };
    writeFileSync(join(resolve(testDir), TEST_CONTEXT_FILE), JSON.stringify(context));
    for (const script of scripts) {
      // Pass trace context to Docker so LLM calls nest under this eval span
      const evalTraceKeys = _setEvalTraceEnv();
      try {
        const results = runEvalInDocker(testDir, validationDir, script, {
          timeout,
          dataDir,
        });
        passed.push(...((results.passed as string[]) || []));
        failed.push(...((results.failed as string[]) || []));
        if (results.error && !results.passed && !results.failed) {
          failed.push(`Test execution error (${script}): ${results.error}`);
        }
      } finally {
        for (const key of evalTraceKeys) {
          delete process.env[key];
        }
      }
    }
    return { passed, failed };
  };
}

/** Run Claude CLI in Docker container. */
export function runClaudeInDocker(
  testDir: string,
  prompt: string,
  options: { timeout?: number; model?: string } = {},
): ShellResult {
  if (!checkDockerAvailable()) throw new Error("Docker not available");

  const { timeout = 300, model } = options;
  const args = [
    "run-claude",
    resolve(testDir),
    prompt,
    "--timeout",
    String(timeout),
  ];
  if (model) args.push("--model", model);

  try {
    return runShell("docker.sh", args, { timeout: timeout + 30, check: false });
  } catch (error) {
    if ((error as Error).message?.includes("ETIMEDOUT")) {
      return {
        stdout: "",
        stderr: `Timeout after ${timeout}s`,
        returncode: 124,
      };
    }
    throw error;
  }
}

// =============================================================================
// SETUP (via setup.sh)
// =============================================================================

export function verifyEnvironment(
  envDir: string,
  requiredFiles = ["Dockerfile", "requirements.txt"],
): boolean {
  return (
    runShell("setup.sh", ["verify", envDir, ...requiredFiles], { check: false })
      .returncode === 0
  );
}

export function createTempDir(prefix = "claude_test_"): string {
  return runShell("setup.sh", ["create-temp", prefix]).stdout.trim();
}

export function cleanupTempDir(dir: string): void {
  runShell("setup.sh", ["cleanup", dir], { check: false });
}

export function writeSkill(
  testDir: string,
  skillName: string,
  contentFile: string,
  scriptsDir?: string,
): string {
  const args = ["write-skill", testDir, skillName, contentFile];
  if (scriptsDir) args.push(scriptsDir);
  return runShell("setup.sh", args).stdout.trim();
}

export function writeClaudeMd(testDir: string, contentFile: string): void {
  runShell("setup.sh", ["write-claude-md", testDir, contentFile]);
}

export function copyEnvironment(testDir: string, envDir: string): void {
  runShell("setup.sh", ["copy-env", testDir, envDir]);
}

// =============================================================================
// HELPERS
// =============================================================================

/** Retry with exponential backoff (for rate limits). */
export async function retryWithBackoff<T>(
  fn: () => T | Promise<T>,
  options: {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
    retryOn?: (e: Error) => boolean;
  } = {},
): Promise<T> {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 10000,
    retryOn = (e) =>
      e.message.includes("429") ||
      e.message.toLowerCase().includes("rate limit"),
  } = options;

  let lastError: Error | undefined;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (!retryOn(lastError) || attempt === maxRetries) throw lastError;
      const delay = Math.min(
        baseDelay * 2 ** attempt + Math.random() * 1000,
        maxDelay,
      );
      await new Promise((r) => setTimeout(r, delay));
    }
  }
  throw lastError;
}

/** Read JSON file. Returns [data, error]. */
export function readJsonFile<T = unknown>(
  path: string,
): [T | null, string | null] {
  if (!existsSync(path)) return [null, `${path} not found`];
  try {
    return [JSON.parse(readFileSync(path, "utf8")) as T, null];
  } catch (error) {
    return [null, `invalid JSON: ${error}`];
  }
}

/** Get first matching field from object. */
export function getField<T>(
  obj: Record<string, unknown>,
  keys: string[],
  defaultValue?: T,
): T | undefined {
  for (const key of keys) if (key in obj) return obj[key] as T;
  return defaultValue;
}

/** Normalize score to 0-1 range. */
export function normalizeScore(score: unknown): number {
  if (typeof score === "boolean") return score ? 1.0 : 0.0;
  if (typeof score === "number") return score > 1 ? score / 100.0 : score;
  return 0.0;
}

// =============================================================================
// LLM EVALUATION (Anthropic SDK)
// =============================================================================

export interface EvalResult {
  pass: boolean;
  reason: string;
}

const EVAL_SYSTEM = `You are an output evaluator. Analyze whether the given output meets the expectations.
Respond with JSON: {"passed": boolean, "reason": "brief explanation"}`;

/** Evaluate output quality using LLM. */
export async function evaluateWithSchema(
  prompt: string,
  options: { model?: string } = {},
): Promise<EvalResult> {
  const model =
    options.model || process.env.BENCH_EVAL_MODEL || "openai:gpt-4o-mini";

  try {
    const Anthropic = (await import("@anthropic-ai/sdk")).default;
    const response = await new Anthropic().messages.create({
      model,
      max_tokens: 256,
      system: EVAL_SYSTEM,
      messages: [{ role: "user", content: prompt }],
    });

    const content = response.content[0];
    if (content.type !== "text")
      return { pass: false, reason: "unexpected response format" };

    const jsonMatch = content.text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) return { pass: false, reason: "no JSON in response" };

    const result = JSON.parse(jsonMatch[0]) as {
      passed: boolean;
      reason: string;
    };
    return { pass: result.passed, reason: result.reason };
  } catch (error) {
    return { pass: false, reason: `eval error: ${String(error).slice(0, 30)}` };
  }
}
