/**
 * Tests for langsmith-trace TypeScript scripts (query_traces.ts).
 *
 * Run with: npx vitest run tests/scripts/langsmith_trace/test_typescript.test.ts
 */

import { describe, it, expect } from "vitest";
import { execSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { SAMPLE_TRACES_LIST, SAMPLE_TRACE_GET } from "../fixtures.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPTS_BASE = resolve(__dirname, "../../../skills/benchmarks");
const SCRIPT_PATH = resolve(
  SCRIPTS_BASE,
  "langsmith_trace-js/scripts/query_traces.ts"
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

describe("langsmith-trace (query_traces.ts)", () => {
  describe("CLI help", () => {
    it("main help", () => {
      const result = runScript(["--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout.toLowerCase()).toContain("traces");
      expect(result.stdout.toLowerCase()).toContain("runs");
    });

    it("traces list help", () => {
      const result = runScript(["traces", "list", "--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("--limit");
      expect(result.stdout).toContain("--project");
    });

    it("traces get help", () => {
      const result = runScript(["traces", "get", "--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("trace-id");
    });

    it("traces export help", () => {
      const result = runScript(["traces", "export", "--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("output-dir");
    });

    it("runs list help", () => {
      const result = runScript(["runs", "list", "--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("--run-type");
    });
  });
});

// =============================================================================
// Fixture validation
// =============================================================================

describe("fixture validation", () => {
  describe("SAMPLE_TRACES_LIST", () => {
    it("has correct structure and exact values", () => {
      expect(SAMPLE_TRACES_LIST.length).toBe(3);

      // Check first trace exact values
      const firstTrace = SAMPLE_TRACES_LIST[0];
      expect(firstTrace.run_id).toBe("019c62bb-d608-74c3-88bd-54d51db3d4a7");
      expect(firstTrace.trace_id).toBe("019c62bb-d608-74c3-88bd-54d51db3d4a7");
      expect(firstTrace.name).toBe("LangGraph");
      expect(firstTrace.run_type).toBe("chain");
      expect(firstTrace.parent_run_id).toBeNull();
      expect(firstTrace.start_time).toBe("2026-02-15T19:16:43.144899");
      expect(firstTrace.end_time).toBe("2026-02-15T19:16:46.686558");

      // Verify all traces have required fields
      for (const trace of SAMPLE_TRACES_LIST) {
        expect(trace).toHaveProperty("run_id");
        expect(trace).toHaveProperty("trace_id");
        expect(trace).toHaveProperty("name");
        expect(trace).toHaveProperty("run_type");
        expect(trace.run_id.length).toBe(36); // UUID format
      }
    });
  });

  describe("SAMPLE_TRACE_GET", () => {
    it("has correct structure and exact values", () => {
      expect(SAMPLE_TRACE_GET.trace_id).toBe(
        "019c62bb-d608-74c3-88bd-54d51db3d4a7"
      );
      expect(SAMPLE_TRACE_GET.run_count).toBe(7);
      expect(SAMPLE_TRACE_GET.runs.length).toBe(7);

      // Check specific runs exist with exact values
      const runNames = SAMPLE_TRACE_GET.runs.map((r) => r.name);
      expect(runNames).toContain("LangGraph");
      expect(runNames).toContain("ChatAnthropic");
      expect(runNames).toContain("calculator");
      expect(runNames).toContain("tools");
      expect(runNames).toContain("model");

      // Check run types
      const runTypes = Object.fromEntries(
        SAMPLE_TRACE_GET.runs.map((r) => [r.name, r.run_type])
      );
      expect(runTypes["LangGraph"]).toBe("chain");
      expect(runTypes["ChatAnthropic"]).toBe("llm");
      expect(runTypes["calculator"]).toBe("tool");

      // Check parent hierarchy (calculator -> tools -> LangGraph)
      const calculatorRun = SAMPLE_TRACE_GET.runs.find(
        (r) => r.name === "calculator"
      )!;
      const toolsRun = SAMPLE_TRACE_GET.runs.find((r) => r.name === "tools")!;
      expect(calculatorRun.parent_run_id).toBe(toolsRun.run_id);
      expect(toolsRun.parent_run_id).toBe(SAMPLE_TRACE_GET.trace_id);
    });
  });
});
