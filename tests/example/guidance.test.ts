/**
 * Example TypeScript benchmark test using Vitest.
 *
 * Demonstrates the test pattern for skill benchmarks:
 * 1. Define treatments (skill configurations to test)
 * 2. Set up test context with skills/CLAUDE.md
 * 3. Run Claude with prompt
 * 4. Parse output and extract events
 * 5. Validate results
 *
 * Run with: npx vitest run tests/example/guidance.test.ts
 * Parallel:  npx vitest run tests/example/guidance.test.ts --pool=threads
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync } from "node:fs";
import {
  setupTest,
  setupTestContext,
  runClaude,
  recordResult,
  finalizeExperiment,
  parseOutput,
  extractEvents,
} from "../fixtures.js";
import type { Treatment } from "../../scaffold/typescript/index.js";
import {
  validate,
  SkillInvokedValidator,
  TypeScriptFileValidator,
  MetricsCollector,
} from "../../scaffold/typescript/index.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

// =============================================================================
// SKILL CONTENT
// =============================================================================

const SKILL_CONTENT = `---
name: ts-patterns
description: Modern TypeScript patterns guide
---

# TypeScript Best Practices

## Interfaces
Always define interfaces for data structures:

\`\`\`typescript
interface User {
  name: string;
  email: string;
  age?: number;
}
\`\`\`

## Functions with Types
Use explicit return types:

\`\`\`typescript
function greet(name: string): string {
  return \`Hello, \${name}!\`;
}
\`\`\`
`;

// =============================================================================
// PROMPT & VALIDATORS
// =============================================================================

const TASK_PROMPT = `Create a simple TypeScript script that:
1. Defines a User interface with name, email, and optional age fields
2. Creates a function that greets a user by name
3. Use explicit types throughout

Save to user_greeting.ts and test it prints a greeting.

IMPORTANT: Run the file directly with tsx. If it fails after 2 attempts, save and report.`;

const REQUIRED_PATTERNS = {
  "interface User": "defines User interface",
  "function greet": "defines greet function",
  ": string": "uses type annotations",
};

function createValidators() {
  return [
    new SkillInvokedValidator("ts-patterns", { required: false }),
    new TypeScriptFileValidator("user_greeting.ts", {
      label: "User Greeting Script",
      required: REQUIRED_PATTERNS,
      requireAll: true,
      runFile: true,
    }),
    new MetricsCollector(["user_greeting.ts"]),
  ];
}

// =============================================================================
// TREATMENTS
// =============================================================================

const TREATMENTS: Record<string, Treatment> = {
  /** Control: No skill provided. Tests baseline model behavior. */
  CONTROL: {
    description: "No skill (pure control)",
    validators: createValidators(),
  },

  /** Baseline: Skill provided. Tests if skill improves code quality. */
  BASELINE: {
    description: "With ts-patterns skill",
    skills: {
      "ts-patterns": [SKILL_CONTENT],
    },
    validators: createValidators(),
  },
};

// =============================================================================
// ENVIRONMENT
// =============================================================================

const ENVIRONMENT_DIR = resolve(
  __dirname,
  "..",
  "langchain_agent",
  "environment"
);

// =============================================================================
// TEST
// =============================================================================

describe("Example Guidance Experiment", () => {
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

  it.for(Object.entries(TREATMENTS))(
    "%s",
    { timeout: 600000 },
    async ([treatmentName, treatment]) => {
      if (!existsSync(ENVIRONMENT_DIR)) {
        expect(true).toBe(true);
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
        events as unknown as Record<string, unknown>,
        testDir,
        {}
      );

      // 5. Record results
      recordResult(logger, treatmentName, events, passed, failed, testDir);

      // 6. Assert
      expect(failed).toEqual([]);
    }
  );
});
