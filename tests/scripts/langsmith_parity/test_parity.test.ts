/**
 * Parity tests - verify Python and TypeScript scripts produce identical output.
 *
 * Run with: npx vitest run tests/scripts/langsmith_parity/test_parity.test.ts
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { execSync } from "node:child_process";
import { mkdtempSync, rmSync, readFileSync, existsSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import {
  createSampleTraceJsonl,
  createSampleDatasetJson,
  SAMPLE_TRACE_RUNS,
  SAMPLE_LOCAL_DATASET,
} from "../fixtures.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPTS_BASE = resolve(__dirname, "../../../skills/benchmarks");

// Script paths
const PY_QUERY_TRACES = resolve(
  SCRIPTS_BASE,
  "langsmith_trace-py/scripts/query_traces.py"
);
const TS_QUERY_TRACES = resolve(
  SCRIPTS_BASE,
  "langsmith_trace-js/scripts/query_traces.ts"
);
const PY_GENERATE_DATASETS = resolve(
  SCRIPTS_BASE,
  "langsmith_dataset-py/scripts/generate_datasets.py"
);
const TS_GENERATE_DATASETS = resolve(
  SCRIPTS_BASE,
  "langsmith_dataset-js/scripts/generate_datasets.ts"
);
const PY_QUERY_DATASETS = resolve(
  SCRIPTS_BASE,
  "langsmith_dataset-py/scripts/query_datasets.py"
);
const TS_QUERY_DATASETS = resolve(
  SCRIPTS_BASE,
  "langsmith_dataset-js/scripts/query_datasets.ts"
);
const PY_UPLOAD_EVALUATORS = resolve(
  SCRIPTS_BASE,
  "langsmith_evaluator-py/scripts/upload_evaluators.py"
);
const TS_UPLOAD_EVALUATORS = resolve(
  SCRIPTS_BASE,
  "langsmith_evaluator-js/scripts/upload_evaluators.ts"
);

/**
 * Run a Python script and return the result.
 */
function runPythonScript(
  scriptPath: string,
  args: string[]
): { stdout: string; stderr: string; returncode: number } {
  try {
    const stdout = execSync(`python ${scriptPath} ${args.join(" ")}`, {
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

/**
 * Run a TypeScript script and return the result.
 */
function runTsScript(
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

/**
 * Normalize JSON data for comparison - sort keys, normalize values.
 */
function normalizeJson(data: unknown): unknown {
  if (typeof data === "object" && data !== null) {
    if (Array.isArray(data)) {
      return data.map(normalizeJson);
    }
    const sorted = Object.keys(data)
      .sort()
      .reduce(
        (acc, key) => {
          acc[key] = normalizeJson((data as Record<string, unknown>)[key]);
          return acc;
        },
        {} as Record<string, unknown>
      );
    return sorted;
  }
  return data;
}

/**
 * Assert two JSON structures are equal after normalization.
 */
function assertJsonEqual(pyData: unknown, tsData: unknown, msg: string): void {
  const pyNormalized = normalizeJson(pyData);
  const tsNormalized = normalizeJson(tsData);
  expect(pyNormalized).toEqual(tsNormalized);
}

describe("CLI help parity", () => {
  it("query_traces help matches", () => {
    const pyResult = runPythonScript(PY_QUERY_TRACES, ["--help"]);
    const tsResult = runTsScript(TS_QUERY_TRACES, ["--help"]);

    expect(pyResult.returncode).toBe(0);
    expect(tsResult.returncode).toBe(0);

    // Both should have same subcommands
    expect(pyResult.stdout.toLowerCase()).toContain("traces");
    expect(tsResult.stdout.toLowerCase()).toContain("traces");
    expect(pyResult.stdout.toLowerCase()).toContain("runs");
    expect(tsResult.stdout.toLowerCase()).toContain("runs");
  });

  it("generate_datasets help matches", () => {
    const pyResult = runPythonScript(PY_GENERATE_DATASETS, ["--help"]);
    const tsResult = runTsScript(TS_GENERATE_DATASETS, ["--help"]);

    expect(pyResult.returncode).toBe(0);
    expect(tsResult.returncode).toBe(0);

    // Both should have same options
    for (const option of ["--input", "--type", "--output"]) {
      expect(pyResult.stdout).toContain(option);
      expect(tsResult.stdout).toContain(option);
    }

    // Both should have same dataset types
    for (const type of ["final_response", "single_step", "trajectory", "rag"]) {
      expect(pyResult.stdout).toContain(type);
      expect(tsResult.stdout).toContain(type);
    }
  });

  it("query_datasets help matches", () => {
    const pyResult = runPythonScript(PY_QUERY_DATASETS, ["--help"]);
    const tsResult = runTsScript(TS_QUERY_DATASETS, ["--help"]);

    expect(pyResult.returncode).toBe(0);
    expect(tsResult.returncode).toBe(0);

    // Both should have same subcommands
    for (const cmd of [
      "list-datasets",
      "show",
      "view-file",
      "structure",
      "export",
    ]) {
      expect(pyResult.stdout).toContain(cmd);
      expect(tsResult.stdout).toContain(cmd);
    }
  });

  it("upload_evaluators help matches", () => {
    const pyResult = runPythonScript(PY_UPLOAD_EVALUATORS, ["--help"]);
    const tsResult = runTsScript(TS_UPLOAD_EVALUATORS, ["--help"]);

    expect(pyResult.returncode).toBe(0);
    expect(tsResult.returncode).toBe(0);

    // Both should have same subcommands
    for (const cmd of ["list", "upload", "delete"]) {
      expect(pyResult.stdout.toLowerCase()).toContain(cmd);
      expect(tsResult.stdout.toLowerCase()).toContain(cmd);
    }
  });
});

describe("generate_datasets output parity", () => {
  let tmpPath: string;

  beforeAll(() => {
    tmpPath = mkdtempSync(join(tmpdir(), "parity_test_"));
  });

  afterAll(() => {
    if (existsSync(tmpPath)) {
      rmSync(tmpPath, { recursive: true });
    }
  });

  it("trajectory output is identical", () => {
    const inputFile = createSampleTraceJsonl(tmpPath);
    const pyOutput = join(tmpPath, `py_trajectory_${Date.now()}.json`);
    const tsOutput = join(tmpPath, `ts_trajectory_${Date.now()}.json`);

    // Run Python
    const pyResult = runPythonScript(PY_GENERATE_DATASETS, [
      "--input",
      inputFile,
      "--type",
      "trajectory",
      "--output",
      pyOutput,
    ]);
    expect(pyResult.returncode).toBe(0);

    // Run TypeScript
    const tsResult = runTsScript(TS_GENERATE_DATASETS, [
      "--input",
      inputFile,
      "--type",
      "trajectory",
      "--output",
      tsOutput,
    ]);
    expect(tsResult.returncode).toBe(0);

    // Compare outputs - EXACT match after normalization
    const pyData = JSON.parse(readFileSync(pyOutput, "utf8"));
    const tsData = JSON.parse(readFileSync(tsOutput, "utf8"));

    expect(pyData.length).toBe(tsData.length);
    expect(pyData.length).toBe(1); // One trace produces one example

    // Exact comparison
    for (let i = 0; i < pyData.length; i++) {
      assertJsonEqual(
        pyData[i],
        tsData[i],
        `Trajectory example ${i} differs between Python and TypeScript`
      );
    }
  });

  it("final_response output is identical", () => {
    const inputFile = createSampleTraceJsonl(tmpPath);
    const pyOutput = join(tmpPath, `py_final_${Date.now()}.json`);
    const tsOutput = join(tmpPath, `ts_final_${Date.now()}.json`);

    // Run Python
    const pyResult = runPythonScript(PY_GENERATE_DATASETS, [
      "--input",
      inputFile,
      "--type",
      "final_response",
      "--output",
      pyOutput,
    ]);
    expect(pyResult.returncode).toBe(0);

    // Run TypeScript
    const tsResult = runTsScript(TS_GENERATE_DATASETS, [
      "--input",
      inputFile,
      "--type",
      "final_response",
      "--output",
      tsOutput,
    ]);
    expect(tsResult.returncode).toBe(0);

    // Compare outputs - EXACT match after normalization
    const pyData = JSON.parse(readFileSync(pyOutput, "utf8"));
    const tsData = JSON.parse(readFileSync(tsOutput, "utf8"));

    expect(pyData.length).toBe(tsData.length);
    expect(pyData.length).toBe(1); // One trace produces one example

    // Exact comparison
    for (let i = 0; i < pyData.length; i++) {
      assertJsonEqual(
        pyData[i],
        tsData[i],
        `Final response example ${i} differs between Python and TypeScript`
      );
    }
  });
});

describe("query_datasets output parity", () => {
  let tmpPath: string;

  beforeAll(() => {
    tmpPath = mkdtempSync(join(tmpdir(), "query_parity_test_"));
  });

  afterAll(() => {
    if (existsSync(tmpPath)) {
      rmSync(tmpPath, { recursive: true });
    }
  });

  it("view-file JSON output is identical", () => {
    const datasetFile = createSampleDatasetJson(tmpPath);

    const pyResult = runPythonScript(PY_QUERY_DATASETS, [
      "view-file",
      datasetFile,
      "--limit",
      "2",
      "--format",
      "json",
    ]);
    const tsResult = runTsScript(TS_QUERY_DATASETS, [
      "view-file",
      datasetFile,
      "--limit",
      "2",
      "--format",
      "json",
    ]);

    expect(pyResult.returncode).toBe(0);
    expect(tsResult.returncode).toBe(0);

    // Extract JSON from output
    const pyJsonStart = pyResult.stdout.indexOf("[");
    const pyJsonEnd = pyResult.stdout.lastIndexOf("]") + 1;
    const tsJsonStart = tsResult.stdout.indexOf("[");
    const tsJsonEnd = tsResult.stdout.lastIndexOf("]") + 1;

    expect(pyJsonStart).toBeGreaterThanOrEqual(0);
    expect(tsJsonStart).toBeGreaterThanOrEqual(0);

    const pyData = JSON.parse(pyResult.stdout.slice(pyJsonStart, pyJsonEnd));
    const tsData = JSON.parse(tsResult.stdout.slice(tsJsonStart, tsJsonEnd));

    // EXACT match
    assertJsonEqual(
      pyData,
      tsData,
      "view-file JSON output differs between Python and TypeScript"
    );
  });

  it("structure output shows same information", () => {
    const datasetFile = createSampleDatasetJson(tmpPath);

    const pyResult = runPythonScript(PY_QUERY_DATASETS, [
      "structure",
      datasetFile,
    ]);
    const tsResult = runTsScript(TS_QUERY_DATASETS, ["structure", datasetFile]);

    expect(pyResult.returncode).toBe(0);
    expect(tsResult.returncode).toBe(0);

    // Both should identify JSON format
    expect(pyResult.stdout).toContain("JSON");
    expect(tsResult.stdout).toContain("JSON");

    // Both should show example count (2)
    expect(pyResult.stdout).toContain("2");
    expect(tsResult.stdout).toContain("2");
  });
});
