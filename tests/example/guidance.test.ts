/**
 * Example TypeScript benchmark test using Vitest.
 *
 * Demonstrates the test pattern for skill benchmarks:
 * 1. Set up test context with skills/CLAUDE.md
 * 2. Run Claude with prompt
 * 3. Parse output and extract events
 * 4. Validate results
 * 5. Record results for reporting
 *
 * Run with: npx vitest run tests/example/guidance.test.ts
 * Parallel:  npx vitest run tests/example/guidance.test.ts --pool=threads
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { existsSync } from "node:fs";
import {
  setupTest,
  setupTestContext,
  runClaude,
  recordResult,
  finalizeExperiment,
  parseOutput,
  extractEvents,
} from "../conftest.js";
import { validate } from "../../scaffold/typescript/index.js";
import { TREATMENTS, TASK_PROMPT, ENVIRONMENT_DIR } from "./config.js";

// =============================================================================
// TEST SETUP
// =============================================================================

describe("Example Guidance Experiment", () => {
  // Skip if environment directory doesn't exist
  beforeAll(() => {
    if (!existsSync(ENVIRONMENT_DIR)) {
      console.warn(
        `Skipping tests: environment directory not found at ${ENVIRONMENT_DIR}`
      );
    }
  });

  afterAll(() => {
    finalizeExperiment();
  });

  // =============================================================================
  // PARAMETERIZED TESTS
  // =============================================================================

  it.each(Object.entries(TREATMENTS))(
    "%s",
    async (treatmentName, treatment) => {
      // Skip if environment doesn't exist
      if (!existsSync(ENVIRONMENT_DIR)) {
        expect(true).toBe(true); // Pass silently
        return;
      }

      // 1. Set up test context
      const { testDir, logger } = setupTest("ts_example");

      setupTestContext(testDir, {
        skills: treatment.skills,
        claudeMd: treatment.claudeMd,
        environmentDir: ENVIRONMENT_DIR,
      });

      // 2. Run Claude
      const result = runClaude(testDir, TASK_PROMPT, {
        timeout: 300,
        logger,
        treatmentName,
      });

      // 3. Parse output and extract events
      const events = extractEvents(parseOutput(result.stdout));

      // 4. Validate
      const { passed, failed } = await validate(
        treatment,
        events as Record<string, unknown>,
        testDir,
        {}
      );

      // 5. Record results
      recordResult(logger, treatmentName, events, passed, failed, testDir);

      // 6. Assert
      expect(failed).toEqual([]);
    },
    { timeout: 600000 } // 10 minute timeout per test
  );
});
