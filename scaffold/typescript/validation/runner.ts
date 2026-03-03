/**
 * Test runner for validation scripts.
 *
 * Handles all boilerplate so contributors just write check functions.
 * Each check function receives a TestRunner and must call runner.passed()
 * or runner.failed() — returning without calling either is an error.
 *
 * Mirrors scaffold/python/validation/runner.py.
 *
 * @example
 * import { TestRunner } from "./scaffold/typescript/validation/runner.js";
 *
 * function checkHasFunction(runner: TestRunner) {
 *   const source = runner.read("agent.ts");
 *   if (source.includes("function myFunction")) {
 *     runner.passed("has myFunction");
 *   } else {
 *     runner.failed("missing myFunction");
 *   }
 * }
 *
 * function checkRuns(runner: TestRunner) {
 *   const output = runner.execute("agent.ts");
 *   if (output !== null) {
 *     runner.passed("produced output");
 *   }
 * }
 *
 * TestRunner.run([checkHasFunction, checkRuns]);
 */

import { existsSync, readFileSync } from "node:fs";
import { execFileSync, execSync } from "node:child_process";
import {
  TEST_CONTEXT_FILE,
  loadTestContext,
  writeTestResults,
} from "./core.js";

export type CheckFn = (runner: TestRunner) => void;

export class TestRunner {
  /** Full run context dict (run_id, events, langsmith_env, etc.) */
  context: Record<string, unknown>;
  /** Target artifact paths from task config */
  artifacts: string[];

  private _passed: string[] = [];
  private _failed: string[] = [];
  private _checkCalled = false;
  private _moduleCache: Map<string, unknown | null> = new Map();

  constructor() {
    this.context = loadTestContext();
    this.artifacts = (this.context.target_artifacts as string[]) || [];
  }

  /** Record a passing check. */
  passed(message: string): void {
    this._checkCalled = true;
    this._passed.push(message);
  }

  /** Record a failing check. */
  failed(message: string): void {
    this._checkCalled = true;
    this._failed.push(message);
  }

  /** Read a file's contents. Returns empty string if not found. */
  read(path: string): string {
    try {
      if (existsSync(path)) {
        return readFileSync(path, "utf8");
      }
    } catch {
      // fall through
    }
    return "";
  }

  /**
   * Import a JS/TS module dynamically. Returns the module or null.
   *
   * Results are cached per path so the module is only imported once.
   * If the import fails, every subsequent call also returns null and
   * records a failure — this ensures each check function that calls
   * loadModule() satisfies TestRunner's passed/failed requirement.
   */
  loadModule(path: string): unknown | null {
    if (this._moduleCache.has(path)) {
      const cached = this._moduleCache.get(path);
      if (cached === null) {
        this.failed(`import failed: ${path} (cached)`);
      }
      return cached ?? null;
    }
    if (!existsSync(path)) {
      this.failed(`cannot load ${path}: file not found`);
      this._moduleCache.set(path, null);
      return null;
    }
    try {
      // Use require for synchronous loading (tsx handles .ts files)
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const mod = require(path);
      this._moduleCache.set(path, mod);
      return mod;
    } catch (e) {
      this.failed(`import error (${path}): ${e}`);
      this._moduleCache.set(path, null);
      return null;
    }
  }

  /**
   * Run a file in a subprocess.
   *
   * Returns stdout on success, stdout+stderr on non-zero exit,
   * or null on failure (also records a failed check).
   */
  execute(
    path: string,
    options: { args?: string[]; timeout?: number } = {},
  ): string | null {
    const { args = [], timeout = 30 } = options;
    if (!existsSync(path)) {
      this.failed(`cannot execute ${path}: file not found`);
      return null;
    }
    const bin = path.endsWith(".py") ? "python3" : "npx";
    const cmdArgs = path.endsWith(".py")
      ? [path, ...args]
      : ["tsx", path, ...args];
    try {
      return execFileSync(bin, cmdArgs, {
        encoding: "utf8",
        timeout: timeout * 1000,
        stdio: ["pipe", "pipe", "pipe"],
      });
    } catch (e: unknown) {
      const err = e as { stdout?: string; stderr?: string; message?: string };
      if (err.stdout || err.stderr) {
        // Non-zero exit — return combined output
        return (err.stdout || "") + (err.stderr || "");
      }
      if (err.message?.includes("ETIMEDOUT") || err.message?.includes("timed out")) {
        this.failed(`execution timed out (${timeout}s)`);
      } else {
        this.failed(`execution error: ${e}`);
      }
      return null;
    }
  }

  private _results(): { passed: string[]; failed: string[]; error: string | null } {
    return {
      passed: this._passed,
      failed: this._failed,
      error: null,
    };
  }

  /**
   * Run check functions and handle all output.
   *
   * Each check function receives a TestRunner instance and MUST call
   * runner.passed() or runner.failed() at least once. Not calling
   * either is treated as an error.
   */
  static run(checks: CheckFn[]): void {
    const runner = new TestRunner();

    if (!runner.context || Object.keys(runner.context).length === 0) {
      console.error(`Error: ${TEST_CONTEXT_FILE} not found or empty`);
      process.exit(1);
    }

    for (const checkFn of checks) {
      const checkName = checkFn.name
        .replace(/^check_?/, "")
        .replace(/([A-Z])/g, " $1")
        .replace(/_/g, " ")
        .trim()
        .toLowerCase();
      runner._checkCalled = false;
      try {
        checkFn(runner);
        if (!runner._checkCalled) {
          runner._failed.push(
            `${checkName}: check did not call passed() or failed()`,
          );
        }
      } catch (e) {
        runner._failed.push(`${checkName}: ${e}`);
      }
    }

    const results = runner._results();
    console.log(JSON.stringify(results, null, 2));
    writeTestResults(results);
    process.exit(results.failed.length > 0 ? 1 : 0);
  }
}
