/**
 * Tests for langsmith-evaluator TypeScript scripts (upload_evaluators.ts).
 *
 * Run with: npx vitest run tests/scripts/langsmith_evaluator/test_typescript.test.ts
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  SAMPLE_EVALUATORS,
  TS_UPLOAD_EVALUATORS,
  runTsScript,
} from "../fixtures.js";

const SCRIPT_PATH = TS_UPLOAD_EVALUATORS;

/**
 * Run the TypeScript script and return the result.
 */
function runScript(args: string[]) {
  return runTsScript(SCRIPT_PATH, args);
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

// =============================================================================
// Mocked API Tests - Direct function imports
// =============================================================================

describe("mocked API functions", () => {
  beforeEach(() => {
    vi.stubEnv("LANGSMITH_API_KEY", "test-api-key-12345");
    vi.stubEnv("LANGSMITH_API_URL", "https://api.smith.langchain.com");
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  describe("getHeaders", () => {
    it("returns correct authentication headers", async () => {
      const { getHeaders } =
        await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

      const headers = getHeaders();

      expect(headers["x-api-key"]).toBe("test-api-key-12345");
      expect(headers["Content-Type"]).toBe("application/json");
    });
  });

  describe("evaluatorExists (mocked)", () => {
    it("returns true when evaluator found in SAMPLE_EVALUATORS", async () => {
      // Mock fetch to return our sample evaluators
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(SAMPLE_EVALUATORS),
      });
      vi.stubGlobal("fetch", mockFetch);

      const { evaluatorExists } =
        await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

      const result = await evaluatorExists("response_quality");
      expect(result).toBe(true);

      vi.unstubAllGlobals();
    });

    it("returns false when evaluator not found", async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(SAMPLE_EVALUATORS),
      });
      vi.stubGlobal("fetch", mockFetch);

      const { evaluatorExists } =
        await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

      const result = await evaluatorExists("nonexistent_evaluator");
      expect(result).toBe(false);

      vi.unstubAllGlobals();
    });

    it("returns false when list is empty", async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([]),
      });
      vi.stubGlobal("fetch", mockFetch);

      const { evaluatorExists } =
        await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

      const result = await evaluatorExists("any_name");
      expect(result).toBe(false);

      vi.unstubAllGlobals();
    });
  });

  describe("createEvaluator (mocked)", () => {
    it("returns true on successful upload", async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
      });
      vi.stubGlobal("fetch", mockFetch);

      const { createEvaluator } =
        await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

      const payload = {
        display_name: "test_evaluator",
        evaluators: [
          {
            code: "function performEval(run, example) { return { score: 1.0 }; }",
            language: "javascript",
          },
        ],
        sampling_rate: 1.0,
      };

      const result = await createEvaluator(payload);
      expect(result).toBe(true);

      // Verify fetch was called correctly
      expect(mockFetch).toHaveBeenCalled();
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain("/runs/rules");
      expect(options.method).toBe("POST");

      vi.unstubAllGlobals();
    });

    it("returns false on upload failure", async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        text: () => Promise.resolve("Bad request"),
      });
      vi.stubGlobal("fetch", mockFetch);

      const { createEvaluator } =
        await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

      const payload = {
        display_name: "test_evaluator",
        evaluators: [{ code: "invalid code", language: "javascript" }],
        sampling_rate: 1.0,
      };

      const result = await createEvaluator(payload);
      expect(result).toBe(false);

      vi.unstubAllGlobals();
    });
  });

  describe("deleteEvaluator (mocked)", () => {
    it("returns false when evaluator not found", async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([]),
      });
      vi.stubGlobal("fetch", mockFetch);

      const { deleteEvaluator } =
        await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

      const result = await deleteEvaluator("nonexistent", false);
      expect(result).toBe(false);

      vi.unstubAllGlobals();
    });

    it("successfully deletes evaluator", async () => {
      // First call returns the list with the evaluator
      // Second call is the DELETE request
      const mockFetch = vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(SAMPLE_EVALUATORS),
        })
        .mockResolvedValueOnce({
          ok: true,
        });
      vi.stubGlobal("fetch", mockFetch);

      const { deleteEvaluator } =
        await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

      const result = await deleteEvaluator("response_quality", false);
      expect(result).toBe(true);

      // Verify DELETE was called with correct URL
      expect(mockFetch).toHaveBeenCalledTimes(2);
      const [deleteUrl] = mockFetch.mock.calls[1];
      expect(deleteUrl).toContain("/runs/rules/");
      expect(deleteUrl).toContain(SAMPLE_EVALUATORS[0].id);

      vi.unstubAllGlobals();
    });
  });
});

// =============================================================================
// Mocked API with Fixtures - Verify data processing
// =============================================================================

describe("mocked API with fixtures", () => {
  beforeEach(() => {
    vi.stubEnv("LANGSMITH_API_KEY", "test-api-key-12345");
    vi.stubEnv("LANGSMITH_API_URL", "https://api.smith.langchain.com");
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
    vi.unstubAllGlobals();
  });

  it("getRules returns data matching SAMPLE_EVALUATORS format", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(SAMPLE_EVALUATORS),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { getRules } =
      await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

    const rules = await getRules();

    // Should return 2 evaluators
    expect(rules.length).toBe(2);

    // First evaluator should match fixture
    expect(rules[0].id).toBe("eval-001-xxxx-xxxx-xxxx-xxxxxxxxxxxx");
    expect(rules[0].display_name).toBe("response_quality");
    expect(rules[0].sampling_rate).toBe(1.0);

    // Second evaluator
    expect(rules[1].display_name).toBe("trajectory_match");
    expect(rules[1].sampling_rate).toBe(0.5);
    expect(rules[1].target_dataset_ids).toEqual(["dataset-001"]);
  });

  it("finds specific evaluators from SAMPLE_EVALUATORS", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(SAMPLE_EVALUATORS),
    });
    vi.stubGlobal("fetch", mockFetch);

    const { evaluatorExists } =
      await import("../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js");

    // response_quality should exist
    expect(await evaluatorExists("response_quality")).toBe(true);

    // trajectory_match should exist
    expect(await evaluatorExists("trajectory_match")).toBe(true);

    // nonexistent should not
    expect(await evaluatorExists("nonexistent")).toBe(false);
  });
});
