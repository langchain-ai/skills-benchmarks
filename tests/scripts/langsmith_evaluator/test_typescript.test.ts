/**
 * Tests for langsmith-evaluator TypeScript scripts (upload_evaluators.ts).
 *
 * Run with: npx vitest run tests/scripts/langsmith/langsmith-evaluator/test_typescript.test.ts
 */

import { describe, it, expect } from "vitest";
import { execSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPTS_BASE = resolve(__dirname, "../../../skills/benchmarks");
const SCRIPT_PATH = resolve(
  SCRIPTS_BASE,
  "langsmith_evaluator-js/scripts/upload_evaluators.ts"
);

/**
 * Run the TypeScript script and return the result.
 */
function runScript(
  args: string[]
): { stdout: string; stderr: string; returncode: number } {
  try {
    const stdout = execSync(`npx tsx ${SCRIPT_PATH} ${args.join(" ")}`, {
      encoding: "utf8",
      timeout: 30000,
      stdio: ["pipe", "pipe", "pipe"],
    });
    return { stdout, stderr: "", returncode: 0 };
  } catch (error) {
    const err = error as { stdout?: string; stderr?: string; status?: number };
    return {
      stdout: err.stdout || "",
      stderr: err.stderr || "",
      returncode: err.status || 1,
    };
  }
}

describe("langsmith-evaluator (upload_evaluators.ts)", () => {
  describe("CLI help", () => {
    it("main help", () => {
      const result = runScript(["--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout.toLowerCase()).toContain("list");
      expect(result.stdout.toLowerCase()).toContain("upload");
      expect(result.stdout.toLowerCase()).toContain("delete");
    });

    it("upload subcommand help", () => {
      const result = runScript(["upload", "--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("--name");
      expect(result.stdout).toContain("--function");
    });

    it("list subcommand help", () => {
      const result = runScript(["list", "--help"]);
      expect(result.returncode).toBe(0);
    });

    it("delete subcommand help", () => {
      const result = runScript(["delete", "--help"]);
      expect(result.returncode).toBe(0);
    });
  });
});
