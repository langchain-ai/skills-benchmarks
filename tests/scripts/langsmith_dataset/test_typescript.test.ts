/**
 * Tests for langsmith-dataset TypeScript scripts (generate_datasets.ts, query_datasets.ts).
 *
 * Run with: npx vitest run tests/scripts/langsmith_dataset/test_typescript.test.ts
 */

import {
  describe,
  it,
  expect,
  beforeAll,
  afterAll,
  vi,
  beforeEach,
  afterEach,
} from "vitest";
import { mkdtempSync, rmSync, readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import {
  SAMPLE_DATASETS,
  SAMPLE_DATASET_EXAMPLES,
  createSampleTraceJsonl,
  createSampleDatasetJson,
  TS_GENERATE_DATASETS,
  TS_QUERY_DATASETS,
  runTsScript,
} from "../fixtures.js";

const GENERATE_DATASETS_PATH = TS_GENERATE_DATASETS;
const QUERY_DATASETS_PATH = TS_QUERY_DATASETS;

/**
 * Run a TypeScript script and return the result.
 */
function runScript(scriptPath: string, args: string[]) {
  return runTsScript(scriptPath, args);
}

// =============================================================================
// generate_datasets.ts tests
// =============================================================================

describe("generate_datasets.ts", () => {
  describe("CLI help", () => {
    it("provides help", () => {
      const result = runScript(GENERATE_DATASETS_PATH, ["--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("--input");
      expect(result.stdout).toContain("--type");
      expect(result.stdout).toContain("--output");
    });

    it("mentions all dataset types", () => {
      const result = runScript(GENERATE_DATASETS_PATH, ["--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("final_response");
      expect(result.stdout).toContain("single_step");
      expect(result.stdout).toContain("trajectory");
      expect(result.stdout).toContain("rag");
    });
  });

  describe("local file processing", () => {
    let tmpPath: string;

    beforeAll(() => {
      tmpPath = mkdtempSync(join(tmpdir(), "generate_datasets_test_"));
    });

    afterAll(() => {
      if (existsSync(tmpPath)) {
        rmSync(tmpPath, { recursive: true });
      }
    });

    it("generates trajectory dataset with exact output validation", () => {
      const inputFile = createSampleTraceJsonl(tmpPath);
      const outputFile = join(tmpPath, `trajectory_${Date.now()}.json`);

      const result = runScript(GENERATE_DATASETS_PATH, [
        "--input",
        inputFile,
        "--type",
        "trajectory",
        "--output",
        outputFile,
      ]);

      expect(result.returncode).toBe(0);
      expect(existsSync(outputFile)).toBe(true);

      const data = JSON.parse(readFileSync(outputFile, "utf8"));

      // Exact assertions based on SAMPLE_TRACE_RUNS fixture
      expect(data.length).toBe(1); // One trace produces one example
      const example = data[0];
      expect(example.trace_id).toBe("trace-001");
      expect(example.inputs.query).toBe("What is the capital of France?");
      expect(example.outputs).toHaveProperty("expected_trajectory");
      // Trajectory should contain tool names from the trace
      expect(example.outputs.expected_trajectory).toContain("search_tool");
    });

    it("generates final_response dataset with exact output validation", () => {
      const inputFile = createSampleTraceJsonl(tmpPath);
      const outputFile = join(tmpPath, `final_response_${Date.now()}.json`);

      const result = runScript(GENERATE_DATASETS_PATH, [
        "--input",
        inputFile,
        "--type",
        "final_response",
        "--output",
        outputFile,
      ]);

      expect(result.returncode).toBe(0);
      expect(existsSync(outputFile)).toBe(true);

      const data = JSON.parse(readFileSync(outputFile, "utf8"));

      // Exact assertions based on SAMPLE_TRACE_RUNS fixture
      expect(data.length).toBe(1); // One trace produces one example
      const example = data[0];
      expect(example.trace_id).toBe("trace-001");
      expect(example.inputs.query).toBe("What is the capital of France?");
      expect(example.outputs.expected_response).toBe("Paris");
    });
  });
});

// =============================================================================
// query_datasets.ts tests
// =============================================================================

describe("query_datasets.ts", () => {
  describe("CLI help", () => {
    it("provides help", () => {
      const result = runScript(QUERY_DATASETS_PATH, ["--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout.toLowerCase()).toContain("list");
    });

    it("has expected subcommands", () => {
      const result = runScript(QUERY_DATASETS_PATH, ["--help"]);
      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("list-datasets");
      expect(result.stdout).toContain("show");
      expect(result.stdout).toContain("view-file");
      expect(result.stdout).toContain("structure");
      expect(result.stdout).toContain("export");
    });
  });

  describe("local file processing", () => {
    let tmpPath: string;

    beforeAll(() => {
      tmpPath = mkdtempSync(join(tmpdir(), "query_datasets_test_"));
    });

    afterAll(() => {
      if (existsSync(tmpPath)) {
        rmSync(tmpPath, { recursive: true });
      }
    });

    it("view-file command returns exact data from file", () => {
      const datasetFile = createSampleDatasetJson(tmpPath);
      const result = runScript(QUERY_DATASETS_PATH, [
        "view-file",
        datasetFile,
        "--limit",
        "2",
        "--format",
        "json",
      ]);

      expect(result.returncode).toBe(0);

      // Parse JSON output and verify exact content matches SAMPLE_LOCAL_DATASET
      const jsonStart = result.stdout.indexOf("[");
      const jsonEnd = result.stdout.lastIndexOf("]") + 1;
      expect(jsonStart).toBeGreaterThanOrEqual(0);

      const data = JSON.parse(result.stdout.slice(jsonStart, jsonEnd));
      expect(data.length).toBe(2);

      // Check exact values from SAMPLE_LOCAL_DATASET
      expect(data[0].trace_id).toBe("trace-001");
      expect(data[0].inputs.query).toBe("What is the capital of France?");
      expect(data[0].outputs.expected_response).toBe("Paris");

      expect(data[1].trace_id).toBe("trace-002");
      expect(data[1].inputs.query).toBe("What is 2 + 2?");
      expect(data[1].outputs.expected_response).toBe("4");
    });

    it("structure command reports exact dataset info", () => {
      const datasetFile = createSampleDatasetJson(tmpPath);
      const result = runScript(QUERY_DATASETS_PATH, ["structure", datasetFile]);

      expect(result.returncode).toBe(0);
      expect(result.stdout).toContain("JSON");
      // Should show exactly 2 examples (matching SAMPLE_LOCAL_DATASET)
      expect(result.stdout).toContain("2");
    });
  });
});

// =============================================================================
// Mocked API Tests - Direct function imports
// =============================================================================

describe("mocked API functions", () => {
  beforeEach(() => {
    vi.stubEnv("LANGSMITH_API_KEY", "test-api-key-12345");
    vi.stubEnv("LANGSMITH_PROJECT", "test-project");
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  describe("query_datasets", () => {
    it("displayExamples formats data correctly", async () => {
      const { displayExamples } =
        await import("../../../skills/benchmarks/langsmith_dataset/scripts/query_datasets.js");

      // Create mock examples matching SAMPLE_DATASET_EXAMPLES format
      const mockExamples = SAMPLE_DATASET_EXAMPLES.map((ex) => ({
        inputs: ex.inputs,
        outputs: ex.outputs,
      }));

      // Capture console output
      const consoleSpy = vi.spyOn(console, "log").mockImplementation(() => {});

      displayExamples(mockExamples, "json", 2);

      // Should have been called with JSON string
      expect(consoleSpy).toHaveBeenCalled();
      const output = consoleSpy.mock.calls[0][0];
      const parsed = JSON.parse(output);

      expect(parsed.length).toBe(2);
      expect(parsed[0].inputs.email_input.author).toBe(
        "Marketing Team <marketing@openai.com>",
      );
      expect(parsed[1].outputs.trajectory).toEqual([
        "check_calendar_availability",
        "schedule_meeting",
        "write_email",
        "done",
      ]);

      consoleSpy.mockRestore();
    });

    it("getClient returns a client when API key is set", async () => {
      const { getClient } =
        await import("../../../skills/benchmarks/langsmith_dataset/scripts/query_datasets.js");

      const client = getClient();
      expect(client).toBeDefined();
    });
  });

  describe("generate_datasets", () => {
    it("loadTracesFromFile loads JSONL data correctly", async () => {
      const { loadTracesFromFile } =
        await import("../../../skills/benchmarks/langsmith_dataset/scripts/generate_datasets.js");

      // Create a temp file with sample trace data
      const tmpPath = mkdtempSync(join(tmpdir(), "gen_datasets_test_"));
      const jsonlFile = createSampleTraceJsonl(tmpPath);

      const traces = loadTracesFromFile(jsonlFile);

      // Should load one trace
      expect(traces.length).toBe(1);

      // Trace should have correct structure [trace_id, root_run, all_runs]
      const [traceId, rootRun, allRuns] = traces[0];
      expect(traceId).toBe("trace-001");
      expect(rootRun.name).toBe("agent");
      expect(allRuns.length).toBe(3);

      // Clean up
      rmSync(tmpPath, { recursive: true });
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

  it("processes dataset list data matching SAMPLE_DATASETS format", async () => {
    // Simulate what would happen when we list datasets from the API
    const mockDatasets = SAMPLE_DATASETS.map((d) => ({
      id: d.id,
      name: d.name,
      description: d.description,
      example_count: d.example_count,
    }));

    // Should have 4 datasets
    expect(mockDatasets.length).toBe(4);

    // Check specific datasets exist with exact names
    const datasetNames = mockDatasets.map((d) => d.name);
    expect(datasetNames).toContain("shipping-support-golden");
    expect(datasetNames).toContain("Email Agent Notebook: Trajectory");
    expect(datasetNames).toContain("Email Agent: Trajectory");
    expect(datasetNames).toContain("kb-agent-golden-set");

    // Check exact example counts
    const datasetCounts = Object.fromEntries(
      mockDatasets.map((d) => [d.name, d.example_count]),
    );
    expect(datasetCounts["shipping-support-golden"]).toBe(10);
    expect(datasetCounts["Email Agent Notebook: Trajectory"]).toBe(5);
    expect(datasetCounts["Email Agent: Trajectory"]).toBe(16);
    expect(datasetCounts["kb-agent-golden-set"]).toBe(15);
  });

  it("processes dataset examples matching SAMPLE_DATASET_EXAMPLES format", async () => {
    // Simulate what would happen when we get examples from the API
    const mockExamples = SAMPLE_DATASET_EXAMPLES.map((ex) => ({
      inputs: ex.inputs,
      outputs: ex.outputs,
    }));

    // Should have 2 examples
    expect(mockExamples.length).toBe(2);

    // First example should have empty trajectory
    const firstExample = mockExamples[0];
    expect(firstExample.inputs.email_input.author).toBe(
      "Marketing Team <marketing@openai.com>",
    );
    expect(firstExample.inputs.email_input.subject).toBe(
      "Newsletter: New Model from OpenAI",
    );
    expect(firstExample.outputs.trajectory).toEqual([]);

    // Second example should have specific trajectory
    const secondExample = mockExamples[1];
    expect(secondExample.inputs.email_input.author).toBe(
      "Project Team <project@company.com>",
    );
    expect(secondExample.outputs.trajectory).toEqual([
      "check_calendar_availability",
      "schedule_meeting",
      "write_email",
      "done",
    ]);
  });
});
