/**
 * Tests for langsmith-evaluator TypeScript scripts (upload_evaluators.ts).
 *
 * Run with: npx vitest run tests/scripts/langsmith_evaluator/test_typescript.test.ts
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { execSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { SAMPLE_EVALUATORS } from "../fixtures.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPTS_BASE = resolve(__dirname, "../../../skills/benchmarks");
const SCRIPT_PATH = resolve(
  SCRIPTS_BASE,
  "langsmith_evaluator/scripts/upload_evaluators.ts"
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
      const { getHeaders, LANGSMITH_API_KEY } = await import(
        "../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js"
      );

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

      const { evaluatorExists } = await import(
        "../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js"
      );

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

      const { evaluatorExists } = await import(
        "../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js"
      );

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

      const { evaluatorExists } = await import(
        "../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js"
      );

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

      const { createEvaluator } = await import(
        "../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js"
      );

      const payload = {
        display_name: "test_evaluator",
        evaluators: [
          {
            code: "def perform_eval(inputs, outputs, reference_outputs):\n    return {'score': 1.0}",
            language: "python",
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

      const { createEvaluator } = await import(
        "../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js"
      );

      const payload = {
        display_name: "test_evaluator",
        evaluators: [{ code: "invalid code", language: "python" }],
        sampling_rate: 1.0,
      };

      const result = await createEvaluator(payload);
      expect(result).toBe(false);

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

    const { getRules } = await import(
      "../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js"
    );

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

    const { evaluatorExists } = await import(
      "../../../skills/benchmarks/langsmith_evaluator/scripts/upload_evaluators.js"
    );

    // response_quality should exist
    expect(await evaluatorExists("response_quality")).toBe(true);

    // trajectory_match should exist
    expect(await evaluatorExists("trajectory_match")).toBe(true);

    // nonexistent should not
    expect(await evaluatorExists("nonexistent")).toBe(false);
  });
});
