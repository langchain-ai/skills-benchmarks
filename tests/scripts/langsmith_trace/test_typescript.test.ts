/**
 * Tests for langsmith-trace TypeScript scripts (query_traces.ts).
 *
 * Run with: npx vitest run tests/scripts/langsmith_trace/test_typescript.test.ts
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { execSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import {
  SAMPLE_TRACES_LIST,
  SAMPLE_TRACE_GET,
  SAMPLE_RUNS_WITH_METADATA,
} from "../fixtures.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPTS_BASE = resolve(__dirname, "../../../skills/benchmarks");
const SCRIPT_PATH = resolve(
  SCRIPTS_BASE,
  "langsmith_trace/scripts/query_traces.ts",
);

/**
 * Run the TypeScript script and return the result.
 */
function runScript(args: string[]): {
  stdout: string;
  stderr: string;
  returncode: number;
} {
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
      // CLI shows traceId (camelCase)
      expect(result.stdout.toLowerCase()).toContain("traceid");
    });

    it("traces export help", () => {
      const result = runScript(["traces", "export", "--help"]);
      expect(result.returncode).toBe(0);
      // CLI shows outputDir (camelCase)
      expect(result.stdout.toLowerCase()).toContain("outputdir");
    });

    it("runs list help", () => {
      const result = runScript(["runs", "list", "--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("--run-type");
    });
  });
});

// =============================================================================
// Mocked API Tests - Direct function imports
// =============================================================================

describe("mocked API functions", () => {
  beforeEach(() => {
    // Set up mock environment
    vi.stubEnv("LANGSMITH_API_KEY", "test-api-key-12345");
    vi.stubEnv("LANGSMITH_PROJECT", "test-project");
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  describe("buildQueryParams", () => {
    it("creates correct params with basic options", async () => {
      const { buildQueryParams } =
        await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

      const params = buildQueryParams({
        project: "my-project",
        limit: 10,
        isRoot: true,
      });

      expect(params.projectName).toBe("my-project");
      expect(params.limit).toBe(10);
      expect(params.isRoot).toBe(true);
    });

    it("handles run type filter", async () => {
      const { buildQueryParams } =
        await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

      const params = buildQueryParams({
        project: "my-project",
        limit: 5,
        runType: "llm",
        isRoot: false,
      });

      expect(params.projectName).toBe("my-project");
      expect(params.limit).toBe(5);
      expect(params.runType).toBe("llm");
      // is_root is only included when True
      expect(params.isRoot).toBeUndefined();
    });

    it("handles error filter", async () => {
      const { buildQueryParams } =
        await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

      const params = buildQueryParams({
        project: "my-project",
        limit: 10,
        isRoot: true,
        error: true,
      });

      expect(params.error).toBe(true);
    });

    it("uses env var when project not specified", async () => {
      const { buildQueryParams } =
        await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

      const params = buildQueryParams({
        limit: 10,
        isRoot: true,
      });

      expect(params.projectName).toBe("test-project");
    });
  });

  describe("extractRun", () => {
    it("extracts basic run data matching fixture format", async () => {
      const { extractRun } =
        await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

      // Create a mock Run object that matches LangSmith SDK structure
      // Use 'as any' since we're only testing the fields extractRun uses
      const mockRun = {
        id: SAMPLE_TRACES_LIST[0].run_id,
        trace_id: SAMPLE_TRACES_LIST[0].trace_id,
        name: SAMPLE_TRACES_LIST[0].name,
        run_type: SAMPLE_TRACES_LIST[0].run_type,
        parent_run_id: SAMPLE_TRACES_LIST[0].parent_run_id,
        start_time: new Date(SAMPLE_TRACES_LIST[0].start_time),
        end_time: new Date(SAMPLE_TRACES_LIST[0].end_time),
      } as any;

      const extracted = extractRun(mockRun, false, false);

      expect(extracted.run_id).toBe(SAMPLE_TRACES_LIST[0].run_id);
      expect(extracted.trace_id).toBe(SAMPLE_TRACES_LIST[0].trace_id);
      expect(extracted.name).toBe("LangGraph");
      expect(extracted.run_type).toBe("chain");
      expect(extracted.parent_run_id).toBeNull();
    });

    it("extracts metadata when requested", async () => {
      const { extractRun } =
        await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

      const runWithMetadata = SAMPLE_RUNS_WITH_METADATA[0];
      const mockRun = {
        id: runWithMetadata.run_id,
        trace_id: runWithMetadata.trace_id,
        name: runWithMetadata.name,
        run_type: runWithMetadata.run_type,
        parent_run_id: runWithMetadata.parent_run_id,
        start_time: new Date(runWithMetadata.start_time),
        end_time: new Date(runWithMetadata.end_time),
        status: runWithMetadata.status,
        extra: { metadata: runWithMetadata.custom_metadata },
        prompt_tokens: runWithMetadata.token_usage?.prompt_tokens,
        completion_tokens: runWithMetadata.token_usage?.completion_tokens,
        total_tokens: runWithMetadata.token_usage?.total_tokens,
      } as any;

      const extracted = extractRun(mockRun, true, false);

      expect(extracted.name).toBe("ChatAnthropic");
      expect(extracted.run_type).toBe("llm");
      expect(extracted.status).toBe("success");
      expect(extracted.custom_metadata).toEqual(
        runWithMetadata.custom_metadata,
      );
      expect(extracted.token_usage?.prompt_tokens).toBe(150);
      expect(extracted.token_usage?.completion_tokens).toBe(75);
      expect(extracted.token_usage?.total_tokens).toBe(225);
    });

    it("extracts inputs/outputs when requested", async () => {
      const { extractRun } =
        await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

      const mockRun = {
        id: "test-run-id",
        trace_id: "test-trace-id",
        name: "test-run",
        run_type: "chain",
        parent_run_id: null,
        start_time: new Date(),
        end_time: new Date(),
        inputs: { query: "What is 2+2?" },
        outputs: { answer: "4" },
      } as any;

      const extracted = extractRun(mockRun, false, true);

      expect(extracted.inputs).toEqual({ query: "What is 2+2?" });
      expect(extracted.outputs).toEqual({ answer: "4" });
    });
  });
});

// =============================================================================
// Mocked API with Fixtures - Verify data processing
// =============================================================================

describe("mocked API with fixtures", () => {
  beforeEach(() => {
    vi.stubEnv("LANGSMITH_API_KEY", "test-api-key-12345");
    vi.stubEnv("LANGSMITH_PROJECT", "test-project");
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("processes trace list data matching SAMPLE_TRACES_LIST format", async () => {
    const { extractRun } =
      await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

    // Simulate processing runs from API response
    // Use 'as any' since we're only testing the fields extractRun uses
    const mockRuns = SAMPLE_TRACES_LIST.map(
      (t) =>
        ({
          id: t.run_id,
          trace_id: t.trace_id,
          name: t.name,
          run_type: t.run_type,
          parent_run_id: t.parent_run_id,
          start_time: new Date(t.start_time),
          end_time: new Date(t.end_time),
        }) as any,
    );

    const extracted = mockRuns.map((r: any) => extractRun(r, false, false));

    // Should return 3 traces
    expect(extracted.length).toBe(3);

    // First trace should match fixture
    expect(extracted[0].name).toBe("LangGraph");
    expect(extracted[0].run_type).toBe("chain");
    expect(extracted[0].parent_run_id).toBeNull();

    // Second trace
    expect(extracted[1].name).toBe("LangGraph");
    expect(extracted[1].trace_id).toBe("019c62bb-92cc-71b0-97e7-8e2b283a432c");

    // Third trace
    expect(extracted[2].name).toBe("LangGraph");
    expect(extracted[2].trace_id).toBe("019c62bb-695f-70e2-a62a-e8fec7118137");
  });

  it("processes trace get data matching SAMPLE_TRACE_GET format", async () => {
    const { extractRun } =
      await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

    // Simulate processing runs from trace get response
    // Use 'as any' since we're only testing the fields extractRun uses
    const mockRuns = SAMPLE_TRACE_GET.runs.map(
      (r) =>
        ({
          id: r.run_id,
          trace_id: r.trace_id,
          name: r.name,
          run_type: r.run_type,
          parent_run_id: r.parent_run_id,
          start_time: new Date(r.start_time),
          end_time: new Date(r.end_time),
        }) as any,
    );

    const extracted = mockRuns.map((r: any) => extractRun(r, false, false));

    // Should return 7 runs in the trace
    expect(extracted.length).toBe(7);

    // Check all expected run names are present
    const runNames = extracted.map((r) => r.name);
    expect(runNames).toContain("LangGraph");
    expect(runNames).toContain("ChatAnthropic");
    expect(runNames).toContain("calculator");
    expect(runNames).toContain("tools");
    expect(runNames).toContain("model");

    // Check run types match fixture
    const runTypes = Object.fromEntries(
      extracted.map((r) => [r.name, r.run_type]),
    );
    expect(runTypes["LangGraph"]).toBe("chain");
    expect(runTypes["ChatAnthropic"]).toBe("llm");
    expect(runTypes["calculator"]).toBe("tool");
  });

  it("processes runs with metadata matching SAMPLE_RUNS_WITH_METADATA format", async () => {
    const { extractRun } =
      await import("../../../skills/benchmarks/langsmith_trace/scripts/query_traces.js");

    // Simulate processing runs with metadata
    // Use 'as any' since we're only testing the fields extractRun uses
    const mockRuns = SAMPLE_RUNS_WITH_METADATA.map(
      (r) =>
        ({
          id: r.run_id,
          trace_id: r.trace_id,
          name: r.name,
          run_type: r.run_type,
          parent_run_id: r.parent_run_id,
          start_time: new Date(r.start_time),
          end_time: new Date(r.end_time),
          status: r.status,
          extra: { metadata: r.custom_metadata },
          prompt_tokens: r.token_usage?.prompt_tokens,
          completion_tokens: r.token_usage?.completion_tokens,
          total_tokens: r.token_usage?.total_tokens,
        }) as any,
    );

    const extracted = mockRuns.map((r: any) => extractRun(r, true, false));

    // Should return 3 runs
    expect(extracted.length).toBe(3);

    // First run should have LLM metadata
    expect(extracted[0].name).toBe("ChatAnthropic");
    expect(extracted[0].run_type).toBe("llm");

    // Check metadata is present
    expect(extracted[0].custom_metadata).toBeDefined();
    expect(extracted[0].custom_metadata?.ls_model_name).toBe(
      "claude-3-5-haiku-20241022",
    );
  });
});
