/**
 * Example experiment configuration.
 *
 * Demonstrates how to define treatments for a TypeScript benchmark test.
 * This is a simplified version of tests/langchain_agent/config.py.
 */

import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { Treatment } from "../../scaffold/typescript/index.js";
import {
  SkillInvokedValidator,
  TypeScriptFileValidator,
  MetricsCollector,
} from "../../scaffold/typescript/index.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

// =============================================================================
// SKILL CONTENT
// =============================================================================

/**
 * Example skill content - teaches modern TypeScript patterns.
 */
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
// PROMPTS
// =============================================================================

export const TASK_PROMPT = `Create a simple TypeScript script that:
1. Defines a User interface with name, email, and optional age fields
2. Creates a function that greets a user by name
3. Use explicit types throughout

Save to user_greeting.ts and test it prints a greeting.

IMPORTANT: Run the file directly with tsx. If it fails after 2 attempts, save and report.`;

// =============================================================================
// VALIDATORS
// =============================================================================

const REQUIRED_PATTERNS = {
  "interface User": "defines User interface",
  "function greet": "defines greet function",
  ": string": "uses type annotations",
};

export function createValidators() {
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

export const TREATMENTS: Record<string, Treatment> = {
  /**
   * Control: No skill provided.
   * Tests baseline model behavior without guidance.
   */
  CONTROL: {
    description: "No skill (pure control)",
    validators: createValidators(),
  },

  /**
   * Baseline: Skill provided.
   * Tests if the skill improves code quality.
   */
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

/**
 * Path to environment directory with Dockerfile, etc.
 * For this example, we use the langchain_agent environment.
 */
export const ENVIRONMENT_DIR = resolve(
  __dirname,
  "..",
  "langchain_agent",
  "environment"
);
