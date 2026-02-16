/**
 * Tests for langsmith-dataset TypeScript scripts (generate_datasets.ts, query_datasets.ts).
 *
 * Run with: npx vitest run tests/scripts/langsmith/langsmith_dataset/test_typescript.test.ts
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { execSync } from "node:child_process";
import { mkdtempSync, rmSync, readFileSync, existsSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import {
  SAMPLE_DATASETS,
  SAMPLE_DATASET_EXAMPLES,
  SAMPLE_TRACE_RUNS,
  SAMPLE_LOCAL_DATASET,
  createSampleTraceJsonl,
  createSampleDatasetJson,
} from "../fixtures.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPTS_BASE = resolve(__dirname, "../../../skills/benchmarks");
const GENERATE_DATASETS_PATH = resolve(
  SCRIPTS_BASE,
  "langsmith_dataset-js/scripts/generate_datasets.ts"
);
const QUERY_DATASETS_PATH = resolve(
  SCRIPTS_BASE,
  "langsmith_dataset-js/scripts/query_datasets.ts"
);

/**
 * Run a TypeScript script and return the result.
 */
function runScript(
  scriptPath: string,
  args: string[]
): { stdout: string; stderr: string; returncode: number } {
  try {
    const stdout = execSync(`npx tsx ${scriptPath} ${args.join(" ")}`, {
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
// Fixture validation
// =============================================================================

describe("fixture validation", () => {
  describe("SAMPLE_DATASETS", () => {
    it("has correct structure and exact values", () => {
      expect(SAMPLE_DATASETS.length).toBe(4);

      // Check specific datasets exist with exact names
      const datasetNames = SAMPLE_DATASETS.map((d) => d.name);
      expect(datasetNames).toContain("shipping-support-golden");
      expect(datasetNames).toContain("Email Agent Notebook: Trajectory");
      expect(datasetNames).toContain("Email Agent: Trajectory");
      expect(datasetNames).toContain("kb-agent-golden-set");

      // Check exact example counts
      const datasetCounts = Object.fromEntries(
        SAMPLE_DATASETS.map((d) => [d.name, d.example_count])
      );
      expect(datasetCounts["shipping-support-golden"]).toBe(10);
      expect(datasetCounts["Email Agent Notebook: Trajectory"]).toBe(5);
      expect(datasetCounts["Email Agent: Trajectory"]).toBe(16);
      expect(datasetCounts["kb-agent-golden-set"]).toBe(15);
    });
  });

  describe("SAMPLE_DATASET_EXAMPLES", () => {
    it("has correct structure and exact values", () => {
      expect(SAMPLE_DATASET_EXAMPLES.length).toBe(2);

      // First example should have empty trajectory
      const firstExample = SAMPLE_DATASET_EXAMPLES[0];
      expect(firstExample.inputs.email_input.author).toBe(
        "Marketing Team <marketing@openai.com>"
      );
      expect(firstExample.inputs.email_input.subject).toBe(
        "Newsletter: New Model from OpenAI"
      );
      expect(firstExample.outputs.trajectory).toEqual([]);

      // Second example should have specific trajectory
      const secondExample = SAMPLE_DATASET_EXAMPLES[1];
      expect(secondExample.inputs.email_input.author).toBe(
        "Project Team <project@company.com>"
      );
      expect(secondExample.inputs.email_input.subject).toBe(
        "Joint presentation next month"
      );
      expect(secondExample.outputs.trajectory).toEqual([
        "check_calendar_availability",
        "schedule_meeting",
        "write_email",
        "done",
      ]);
    });
  });
});
