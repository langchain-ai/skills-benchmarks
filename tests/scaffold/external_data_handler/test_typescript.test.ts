/**
 * Unit tests for external_data_handler module with mocked LangSmith client.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

// Create mock client that persists across tests
const mockClient = {
  createRun: vi.fn().mockResolvedValue(undefined),
  updateRun: vi.fn().mockResolvedValue(undefined),
  createDataset: vi.fn().mockResolvedValue({ id: "dataset-123" }),
  createExamples: vi.fn().mockResolvedValue(undefined),
  listProjects: vi.fn(),
  listDatasets: vi.fn(),
  deleteProject: vi.fn().mockResolvedValue(undefined),
  deleteDataset: vi.fn().mockResolvedValue(undefined),
};

// Mock the langsmith module
vi.mock("langsmith", () => ({
  Client: vi.fn(() => mockClient),
}));

// Import after mocking
import {
  uploadTraces,
  uploadDatasets,
  cleanupNamespace,
  runHandler,
  runTaskHandlers,
} from "../../../scaffold/typescript/external_data_handler.js";

// =============================================================================
// FIXTURES
// =============================================================================

function createTraceDataDir(): string {
  const dir = mkdtempSync(join(tmpdir(), "trace_test_"));
  const traceFile = join(dir, "trace_001.jsonl");
  const operations = [
    {
      operation: "post",
      id: "run-001",
      name: "root_run",
      run_type: "chain",
      inputs: { messages: [{ content: "Hello world" }] },
      start_time: "2024-01-01T00:00:00Z",
      parent_run_id: null,
    },
    {
      operation: "post",
      id: "run-002",
      name: "child_run",
      run_type: "llm",
      inputs: {},
      start_time: "2024-01-01T00:00:01Z",
      parent_run_id: "run-001",
    },
    {
      operation: "patch",
      id: "run-002",
      end_time: "2024-01-01T00:00:02Z",
      outputs: { result: "success" },
    },
    {
      operation: "patch",
      id: "run-001",
      end_time: "2024-01-01T00:00:03Z",
      outputs: { answer: "Hello!" },
    },
  ];
  writeFileSync(traceFile, operations.map((op) => JSON.stringify(op)).join("\n"));
  return dir;
}

function createDatasetDataDir(): string {
  const dir = mkdtempSync(join(tmpdir(), "dataset_test_"));

  // SQL dataset
  const sqlFile = join(dir, "sql_agent_dataset.json");
  writeFileSync(
    sqlFile,
    JSON.stringify([
      { inputs: { query: "SELECT * FROM users" }, outputs: { result: [] } },
      { inputs: { query: "SELECT COUNT(*)" }, outputs: { result: [10] } },
    ])
  );

  // Trajectory dataset
  const trajFile = join(dir, "trajectory_dataset.json");
  writeFileSync(trajFile, JSON.stringify([{ inputs: { x: 1 }, outputs: { y: 2 } }]));

  return dir;
}

// =============================================================================
// TESTS
// =============================================================================

describe("external_data_handler", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset async iterator mocks
    mockClient.listProjects.mockImplementation(async function* () {});
    mockClient.listDatasets.mockImplementation(async function* () {});
  });

  describe("uploadTraces", () => {
    it("uploads traces from jsonl files", async () => {
      const dataDir = createTraceDataDir();

      try {
        const result = await uploadTraces({
          project: "test-project",
          data_dir: dataDir,
        });

        expect(mockClient.createRun).toHaveBeenCalled();
        // Should return mapping of old ID to new ID
        expect(result).toHaveProperty("run-001");
      } finally {
        rmSync(dataDir, { recursive: true, force: true });
      }
    });

    it("handles empty directory", async () => {
      const emptyDir = mkdtempSync(join(tmpdir(), "empty_"));

      try {
        const result = await uploadTraces({
          project: "test-project",
          data_dir: emptyDir,
        });

        expect(result).toEqual({});
        expect(mockClient.createRun).not.toHaveBeenCalled();
      } finally {
        rmSync(emptyDir, { recursive: true, force: true });
      }
    });

    it("handles nonexistent directory", async () => {
      const result = await uploadTraces({
        project: "test-project",
        data_dir: "/nonexistent/path",
      });

      expect(result).toEqual({});
    });
  });

  describe("uploadDatasets", () => {
    it("uploads datasets with naming convention", async () => {
      const dataDir = createDatasetDataDir();

      try {
        const result = await uploadDatasets({
          data_dir: dataDir,
          run_id: "abc123",
        });

        // Should create datasets for both files
        expect(mockClient.createDataset).toHaveBeenCalledTimes(2);
        expect(mockClient.createExamples).toHaveBeenCalledTimes(2);

        // Check naming convention: bench-{type}-{run_id}
        expect(result["sql_agent_dataset.json"]).toBe("bench-sql-abc123");
        expect(result["trajectory_dataset.json"]).toBe("bench-trajectory-abc123");
      } finally {
        rmSync(dataDir, { recursive: true, force: true });
      }
    });

    it("handles single example (not array)", async () => {
      const dir = mkdtempSync(join(tmpdir(), "single_"));
      const singleFile = join(dir, "test_dataset.json");
      writeFileSync(singleFile, JSON.stringify({ inputs: { x: 1 }, outputs: { y: 2 } }));

      try {
        await uploadDatasets({
          data_dir: dir,
          run_id: "xyz",
        });

        expect(mockClient.createDataset).toHaveBeenCalled();
        expect(mockClient.createExamples).toHaveBeenCalledWith(
          expect.objectContaining({
            inputs: [{ x: 1 }],
            outputs: [{ y: 2 }],
          })
        );
      } finally {
        rmSync(dir, { recursive: true, force: true });
      }
    });

    it("requires run_id", async () => {
      const dataDir = createDatasetDataDir();

      try {
        const result = await uploadDatasets({
          data_dir: dataDir,
          // no run_id
        });

        expect(result).toEqual({});
        expect(mockClient.createDataset).not.toHaveBeenCalled();
      } finally {
        rmSync(dataDir, { recursive: true, force: true });
      }
    });
  });

  describe("cleanupNamespace", () => {
    it("deletes matching projects and datasets", async () => {
      // Setup mock async iterators
      const mockProjects = [
        { name: "bench-test-run123" },
        { name: "other-project" },
      ];
      const mockDatasets = [
        { name: "bench-sql-run123" },
        { name: "unrelated-dataset" },
      ];

      mockClient.listProjects.mockImplementation(async function* () {
        for (const p of mockProjects) yield p;
      });
      mockClient.listDatasets.mockImplementation(async function* () {
        for (const d of mockDatasets) yield d;
      });

      const result = await cleanupNamespace({ run_id: "run123" });

      // Should only delete resources ending with -run123
      expect(mockClient.deleteProject).toHaveBeenCalledTimes(1);
      expect(mockClient.deleteDataset).toHaveBeenCalledTimes(1);
      expect(result.projects).toContain("bench-test-run123");
      expect(result.datasets).toContain("bench-sql-run123");
    });

    it("handles no matching resources", async () => {
      const result = await cleanupNamespace({ run_id: "nonexistent" });

      expect(result).toEqual({ projects: [], datasets: [] });
    });

    it("requires run_id", async () => {
      const result = await cleanupNamespace({});

      expect(result).toEqual({ projects: [], datasets: [] });
      expect(mockClient.listProjects).not.toHaveBeenCalled();
    });
  });

  describe("runHandler", () => {
    it("runs registered handler", async () => {
      const result = await runHandler("cleanup_namespace", { run_id: "test123" });

      expect(result).toEqual({ projects: [], datasets: [] });
    });

    it("throws for unknown handler", async () => {
      await expect(runHandler("nonexistent_handler", {})).rejects.toThrow("Unknown handler");
    });
  });

  describe("runTaskHandlers", () => {
    it("runs matching handlers", async () => {
      const dataDir = createTraceDataDir();

      try {
        const handlers = [
          { pattern: "trace_*.jsonl", handler: "upload_traces", args: {} },
        ];

        const result = await runTaskHandlers(handlers, dataDir, "test-project", "abc");

        expect(mockClient.createRun).toHaveBeenCalled();
        // upload_traces returns trace ID mapping
        expect(typeof result).toBe("object");
      } finally {
        rmSync(dataDir, { recursive: true, force: true });
      }
    });

    it("skips handlers with no matching files", async () => {
      const emptyDir = mkdtempSync(join(tmpdir(), "empty_"));

      try {
        const handlers = [
          { pattern: "nonexistent_*.json", handler: "upload_traces" },
        ];

        const result = await runTaskHandlers(handlers, emptyDir, "test", "abc");

        expect(mockClient.createRun).not.toHaveBeenCalled();
        expect(result).toEqual({});
      } finally {
        rmSync(emptyDir, { recursive: true, force: true });
      }
    });

    it("handles nonexistent data dir", async () => {
      const handlers = [{ pattern: "*.json", handler: "upload_traces" }];

      const result = await runTaskHandlers(handlers, "/nonexistent/path", "test", "abc");

      expect(result).toEqual({});
    });

    it("passes handler args", async () => {
      const dataDir = createDatasetDataDir();

      try {
        const handlers = [
          { pattern: "*_dataset.json", handler: "upload_datasets", args: { extra_arg: "value" } },
        ];

        await runTaskHandlers(handlers, dataDir, "test", "xyz");

        expect(mockClient.createDataset).toHaveBeenCalled();
      } finally {
        rmSync(dataDir, { recursive: true, force: true });
      }
    });
  });

  // =========================================================================
  // REGRESSION TESTS - Verify incorrect implementations would fail
  // =========================================================================

  describe("regression cases", () => {
    it("upload_traces requires post operations", async () => {
      const dir = mkdtempSync(join(tmpdir(), "no_post_"));
      const traceFile = join(dir, "trace_001.jsonl");
      // Only patch operations, no post
      writeFileSync(
        traceFile,
        JSON.stringify({ operation: "patch", id: "run-001", outputs: {} })
      );

      try {
        const result = await uploadTraces({
          project: "test-project",
          data_dir: dir,
        });

        // Should not crash, should return empty mapping
        expect(result).toEqual({});
      } finally {
        rmSync(dir, { recursive: true, force: true });
      }
    });

    it("cleanup suffix matching is exact", async () => {
      // "bench-run123-extra" contains "-run123" but doesn't END with it
      // Should NOT be deleted when cleaning up run123
      const mockProjects = [{ name: "bench-run123-extra" }];

      mockClient.listProjects.mockImplementation(async function* () {
        for (const p of mockProjects) yield p;
      });
      mockClient.listDatasets.mockImplementation(async function* () {});

      const result = await cleanupNamespace({ run_id: "run123" });

      // Should NOT delete - suffix is in middle, not at end
      expect(mockClient.deleteProject).not.toHaveBeenCalled();
      expect(result.projects).toEqual([]);
    });

    it("dataset naming extracts first underscore segment", async () => {
      const dir = mkdtempSync(join(tmpdir(), "naming_"));
      // mytype_other_parts_dataset.json should become bench-mytype-{run_id}
      const datasetFile = join(dir, "mytype_other_parts_dataset.json");
      writeFileSync(datasetFile, JSON.stringify([{ inputs: {}, outputs: {} }]));

      try {
        const result = await uploadDatasets({
          data_dir: dir,
          run_id: "abc",
        });

        expect(result["mytype_other_parts_dataset.json"]).toBe("bench-mytype-abc");
      } finally {
        rmSync(dir, { recursive: true, force: true });
      }
    });

    it("id mapping preserves parent-child relationships", async () => {
      const dir = mkdtempSync(join(tmpdir(), "parent_child_"));
      const traceFile = join(dir, "trace_001.jsonl");
      const operations = [
        {
          operation: "post",
          id: "parent-id",
          name: "parent",
          run_type: "chain",
          inputs: {},
          start_time: "2024-01-01T00:00:00Z",
        },
        {
          operation: "post",
          id: "child-id",
          name: "child",
          run_type: "llm",
          inputs: {},
          start_time: "2024-01-01T00:00:01Z",
          parent_run_id: "parent-id",
        },
      ];
      writeFileSync(traceFile, operations.map((op) => JSON.stringify(op)).join("\n"));

      try {
        await uploadTraces({ project: "test-project", data_dir: dir });

        // Verify child's parent_run_id was remapped (not the old ID)
        const calls = mockClient.createRun.mock.calls;
        expect(calls.length).toBe(2);

        // Find the child call (has parent_run_id)
        const childCall = calls.find((c: unknown[]) => (c[0] as Record<string, unknown>).parent_run_id);
        expect(childCall).toBeDefined();
        // Parent ID should have been remapped (not "parent-id")
        expect((childCall![0] as Record<string, unknown>).parent_run_id).not.toBe("parent-id");
      } finally {
        rmSync(dir, { recursive: true, force: true });
      }
    });

    it("time shifting preserves relative ordering", async () => {
      const dir = mkdtempSync(join(tmpdir(), "time_shift_"));
      const traceFile = join(dir, "trace_001.jsonl");
      const operations = [
        {
          operation: "post",
          id: "run-1",
          name: "first",
          run_type: "chain",
          inputs: {},
          start_time: "2024-01-01T00:00:00Z",
        },
        {
          operation: "post",
          id: "run-2",
          name: "second",
          run_type: "chain",
          inputs: {},
          start_time: "2024-01-01T00:01:00Z", // 1 minute later
        },
      ];
      writeFileSync(traceFile, operations.map((op) => JSON.stringify(op)).join("\n"));

      try {
        await uploadTraces({ project: "test-project", data_dir: dir });

        const calls = mockClient.createRun.mock.calls;
        const times = calls.map((c: unknown[]) => {
          const st = (c[0] as Record<string, unknown>).start_time;
          return new Date(st as string);
        });

        // The difference should still be ~1 minute
        const delta = Math.abs(times[1].getTime() - times[0].getTime()) / 1000;
        expect(delta).toBeGreaterThan(55);
        expect(delta).toBeLessThan(65);
      } finally {
        rmSync(dir, { recursive: true, force: true });
      }
    });
  });
});
