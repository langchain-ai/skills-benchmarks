/**
 * Example TypeScript benchmark test using Vitest.
 *
 * Demonstrates the test pattern for skill benchmarks:
 * 1. Load skills from skill.md files using parser
 * 2. Define treatments (skill configurations to test)
 * 3. Set up test context with skills/CLAUDE.md
 * 4. Run Claude with prompt
 * 5. Parse output and extract events
 * 6. Validate results
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
  FileValidator,
  MetricsCollector,
} from "../../scaffold/typescript/index.js";
import { loadSkill } from "../../skills/parser.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_BASE = resolve(__dirname, "../../skills/benchmarks");

// =============================================================================
// LOAD SKILLS
// =============================================================================

// Load skill from skill.md file - provides .all (all sections) and .sections (by tag)
const langchainSkill = loadSkill(resolve(SKILL_BASE, "langchain_basic"));

// =============================================================================
// PROMPT & VALIDATORS
// =============================================================================

const TASK_PROMPT = `Create a simple LangChain agent that:
1. Uses the @tool decorator to define a calculator tool
2. Uses create_agent to build the agent
3. Invokes the agent with a test question

Save to agent.py and run it.`;

const REQUIRED_PATTERNS = {
  "@tool": "uses @tool decorator",
  create_agent: "uses create_agent",
};

function createValidators() {
  return [
    new SkillInvokedValidator("langchain-agents", { required: false }),
    new FileValidator("agent.py", {
      label: "LangChain Agent",
      required: REQUIRED_PATTERNS,
      requireAll: true,
    }),
    new MetricsCollector(["agent.py"]),
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

  /** All sections: Full skill content. */
  ALL_SECTIONS: {
    description: "With langchain-agents skill (all sections)",
    skills: {
      // Use all sections from the skill
      "langchain-agents": langchainSkill.all,
    },
    validators: createValidators(),
  },

  /** Minimal: Only specific sections. Tests minimal guidance. */
  MINIMAL: {
    description: "With langchain-agents skill (minimal sections)",
    skills: {
      // Select specific sections by tag name
      "langchain-agents": [
        langchainSkill.sections["frontmatter"],
        langchainSkill.sections["oneliner"],
        langchainSkill.sections["quick_start"],
      ],
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
  "benchmarks",
  "lc_basic",
  "environment",
);

// =============================================================================
// TEST
// =============================================================================

describe("Example Guidance Experiment", () => {
  beforeAll(() => {
    if (!existsSync(ENVIRONMENT_DIR)) {
      console.warn(
        `Skipping tests: environment directory not found at ${ENVIRONMENT_DIR}`,
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
        {},
      );

      // 5. Record results
      recordResult(logger, treatmentName, events, passed, failed, testDir);

      // 6. Assert
      expect(failed).toEqual([]);
    },
  );
});
