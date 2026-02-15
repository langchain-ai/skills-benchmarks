/**
 * TypeScript utilities - thin wrappers around shell scripts.
 *
 * Mirrors scaffold/python/utils.py - shell scripts (scaffold/shell/) are the source of truth.
 */

import { execSync, type ExecSyncOptions } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { config as loadEnv } from "dotenv";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SHELL_DIR = resolve(__dirname, "..", "shell");
const PROJECT_ROOT = resolve(__dirname, "..", "..");

// Load .env file
loadEnv({ path: join(PROJECT_ROOT, ".env") });

// =============================================================================
// SHELL SCRIPT RUNNER
// =============================================================================

export interface ShellResult {
  stdout: string;
  stderr: string;
  returncode: number;
}

/**
 * Run a shell script from scaffold/shell/.
 */
export function runShell(
  script: string,
  args: string[] = [],
  options: {
    timeout?: number;
    check?: boolean;
    cwd?: string;
  } = {}
): ShellResult {
  const { timeout, check = true, cwd } = options;
  const cmd = ["bash", join(SHELL_DIR, script), ...args].join(" ");

  const execOptions: ExecSyncOptions = {
    encoding: "utf8",
    stdio: ["pipe", "pipe", "pipe"],
    timeout: timeout ? timeout * 1000 : undefined,
    cwd,
    env: process.env,
  };

  try {
    const stdout = execSync(cmd, execOptions) as string;
    return { stdout, stderr: "", returncode: 0 };
  } catch (error: unknown) {
    const execError = error as {
      stdout?: Buffer | string;
      stderr?: Buffer | string;
      status?: number;
    };
    const stdout = execError.stdout?.toString() || "";
    const stderr = execError.stderr?.toString() || "";
    const returncode = execError.status ?? 1;

    if (check) {
      throw new Error(`Shell command failed: ${cmd}\n${stderr}`);
    }
    return { stdout, stderr, returncode };
  }
}

// =============================================================================
// DOCKER (via docker.sh)
// =============================================================================

/**
 * Check if Docker is available.
 */
export function checkDockerAvailable(): boolean {
  try {
    const result = runShell("docker.sh", ["check"], { check: false, timeout: 10 });
    return result.returncode === 0;
  } catch {
    return false;
  }
}

/**
 * Check if Claude CLI is available.
 */
export function checkClaudeAvailable(): boolean {
  try {
    execSync("claude --version", { stdio: "pipe", timeout: 10000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Build Docker image (cached by Dockerfile hash).
 */
export function buildDockerImage(
  testDir: string,
  options: { force?: boolean } = {}
): string | null {
  try {
    const args = ["build", resolve(testDir)];
    if (options.force) {
      args.push("--force");
    }
    const result = runShell("docker.sh", args, { timeout: 300, check: false });
    return result.returncode === 0 ? result.stdout.trim() : null;
  } catch {
    return null;
  }
}

/**
 * Run command in Docker container.
 */
export function runInDocker(
  testDir: string,
  command: string[],
  options: {
    timeout?: number;
    envVars?: Record<string, string>;
  } = {}
): ShellResult {
  const { timeout = 120, envVars } = options;

  // Set environment variables
  const oldEnv: Record<string, string | undefined> = {};
  if (envVars) {
    for (const [key, value] of Object.entries(envVars)) {
      oldEnv[key] = process.env[key];
      process.env[key] = value;
    }
  }

  try {
    return runShell("docker.sh", ["run", resolve(testDir), ...command], {
      timeout,
      check: false,
    });
  } finally {
    // Restore environment
    for (const [key, value] of Object.entries(oldEnv)) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
  }
}

/**
 * Run Python script in Docker. Returns [success, output].
 */
export function runPythonInDocker(
  testDir: string,
  scriptName: string,
  options: {
    timeout?: number;
    args?: string[];
  } = {}
): [boolean, string] {
  const { timeout = 120, args = [] } = options;

  if (!checkDockerAvailable()) {
    return [false, "Docker not available"];
  }

  try {
    const cmdArgs = ["run-python", resolve(testDir), scriptName, ...args];
    const result = runShell("docker.sh", cmdArgs, { timeout, check: false });
    return [result.returncode === 0, result.stdout + result.stderr];
  } catch (error) {
    if ((error as Error).message?.includes("ETIMEDOUT")) {
      return [false, `Timeout (${timeout}s)`];
    }
    return [false, String(error)];
  }
}

/**
 * Run Node.js/TypeScript script in Docker. Returns [success, output].
 */
export function runNodeInDocker(
  testDir: string,
  scriptName: string,
  options: {
    timeout?: number;
    args?: string[];
  } = {}
): [boolean, string] {
  const { timeout = 120, args = [] } = options;

  if (!checkDockerAvailable()) {
    return [false, "Docker not available"];
  }

  try {
    const cmdArgs = ["run-node", resolve(testDir), scriptName, ...args];
    const result = runShell("docker.sh", cmdArgs, { timeout, check: false });
    return [result.returncode === 0, result.stdout + result.stderr];
  } catch (error) {
    if ((error as Error).message?.includes("ETIMEDOUT")) {
      return [false, `Timeout (${timeout}s)`];
    }
    return [false, String(error)];
  }
}

/**
 * Run script in Docker based on file extension. Returns [success, output].
 */
export function runScriptInDocker(
  testDir: string,
  scriptName: string,
  options: {
    timeout?: number;
    args?: string[];
  } = {}
): [boolean, string] {
  if (scriptName.endsWith(".py")) {
    return runPythonInDocker(testDir, scriptName, options);
  } else if (scriptName.endsWith(".ts") || scriptName.endsWith(".js")) {
    return runNodeInDocker(testDir, scriptName, options);
  }
  return [false, `Unsupported file type: ${scriptName}`];
}

/**
 * Run Claude CLI in Docker container.
 */
export function runClaudeInDocker(
  testDir: string,
  prompt: string,
  options: {
    timeout?: number;
    model?: string;
  } = {}
): ShellResult {
  const { timeout = 300, model } = options;

  if (!checkDockerAvailable()) {
    throw new Error("Docker not available");
  }

  const cmdArgs = [
    "run-claude",
    resolve(testDir),
    prompt,
    "--timeout",
    String(timeout),
  ];
  if (model) {
    cmdArgs.push("--model", model);
  }

  try {
    return runShell("docker.sh", cmdArgs, { timeout: timeout + 30, check: false });
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

/**
 * Verify environment (Docker, Claude CLI, API keys).
 */
export function verifyEnvironment(
  envDir: string,
  requiredFiles: string[] = ["Dockerfile", "requirements.txt"]
): boolean {
  const result = runShell("setup.sh", ["verify", envDir, ...requiredFiles], {
    check: false,
  });
  return result.returncode === 0;
}

/**
 * Create a temporary directory.
 */
export function createTempDir(prefix = "claude_test_"): string {
  const result = runShell("setup.sh", ["create-temp", prefix]);
  return result.stdout.trim();
}

/**
 * Cleanup a temporary directory.
 */
export function cleanupTempDir(dir: string): void {
  runShell("setup.sh", ["cleanup", dir], { check: false });
}

/**
 * Write a skill to .claude/skills/.
 */
export function writeSkill(
  testDir: string,
  skillName: string,
  contentFile: string,
  scriptsDir?: string
): string {
  const args = ["write-skill", testDir, skillName, contentFile];
  if (scriptsDir) {
    args.push(scriptsDir);
  }
  const result = runShell("setup.sh", args);
  return result.stdout.trim();
}

/**
 * Write CLAUDE.md to .claude/.
 */
export function writeClaudeMd(testDir: string, contentFile: string): void {
  runShell("setup.sh", ["write-claude-md", testDir, contentFile]);
}

/**
 * Copy environment files to test directory.
 */
export function copyEnvironment(testDir: string, envDir: string): void {
  runShell("setup.sh", ["copy-env", testDir, envDir]);
}

// =============================================================================
// HELPERS
// =============================================================================

/**
 * Retry with exponential backoff.
 */
export async function retryWithBackoff<T>(
  fn: () => T | Promise<T>,
  options: {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
    retryOn?: (error: Error) => boolean;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 10000,
    retryOn = (e) => e.message.includes("429") || e.message.toLowerCase().includes("rate limit"),
  } = options;

  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (!retryOn(lastError) || attempt === maxRetries) {
        throw lastError;
      }
      const delay = Math.min(baseDelay * Math.pow(2, attempt) + Math.random() * 1000, maxDelay);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

/**
 * Read JSON file. Returns [data, error].
 */
export function readJsonFile<T = unknown>(path: string): [T | null, string | null] {
  if (!existsSync(path)) {
    return [null, `${path} not found`];
  }
  try {
    const content = readFileSync(path, "utf8");
    return [JSON.parse(content) as T, null];
  } catch (error) {
    return [null, `invalid JSON: ${error}`];
  }
}

/**
 * Get first matching field from object.
 */
export function getField<T>(
  obj: Record<string, unknown>,
  keys: string[],
  defaultValue?: T
): T | undefined {
  for (const key of keys) {
    if (key in obj) {
      return obj[key] as T;
    }
  }
  return defaultValue;
}

/**
 * Normalize score to 0-1 range.
 */
export function normalizeScore(score: unknown): number {
  if (typeof score === "boolean") {
    return score ? 1.0 : 0.0;
  }
  if (typeof score === "number" && score > 1) {
    return score / 100.0;
  }
  return typeof score === "number" ? score : 0.0;
}

// =============================================================================
// LLM EVALUATION (native JS with Anthropic SDK)
// =============================================================================

export interface EvalResult {
  pass: boolean;
  reason: string;
}

/**
 * Evaluate with structured output using Anthropic SDK.
 * Returns { pass: boolean, reason: string }.
 */
export async function evaluateWithSchema(
  prompt: string,
  options: {
    model?: string;
  } = {}
): Promise<EvalResult> {
  const { model = process.env.EVAL_MODEL || "claude-sonnet-4-20250514" } = options;

  try {
    const Anthropic = (await import("@anthropic-ai/sdk")).default;
    const client = new Anthropic();

    const systemPrompt = `You are an output evaluator. Analyze whether the given output meets the expectations.
Respond with JSON in this exact format: {"passed": boolean, "reason": "brief explanation"}`;

    const response = await client.messages.create({
      model,
      max_tokens: 256,
      system: systemPrompt,
      messages: [{ role: "user", content: prompt }],
    });

    const content = response.content[0];
    if (content.type !== "text") {
      return { pass: false, reason: "unexpected response format" };
    }

    // Parse JSON from response
    const jsonMatch = content.text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      return { pass: false, reason: "no JSON in response" };
    }

    const result = JSON.parse(jsonMatch[0]) as { passed: boolean; reason: string };
    return { pass: result.passed, reason: result.reason };
  } catch (error) {
    return { pass: false, reason: `eval error: ${String(error).slice(0, 30)}` };
  }
}
