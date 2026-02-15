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
  PythonFileValidator,
  MetricsCollector,
} from "../../scaffold/typescript/index.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

// =============================================================================
// SKILL CONTENT
// =============================================================================

/**
 * Example skill content - teaches modern Python patterns.
 */
const SKILL_CONTENT = `---
name: python-patterns
description: Modern Python patterns guide
---

# Python Best Practices

## Type Hints
Always use type hints for function signatures:

\`\`\`python
def greet(name: str) -> str:
    return f"Hello, {name}!"
\`\`\`

## Dataclasses
Use dataclasses for data containers:

\`\`\`python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int = 0
\`\`\`
`;

// =============================================================================
// PROMPTS
// =============================================================================

export const TASK_PROMPT = `Create a simple Python script that:
1. Defines a User dataclass with name, email, and age fields
2. Creates a function that greets a user by name
3. Use type hints throughout

Save to user_greeting.py and test it prints a greeting.

IMPORTANT: Run the file directly. If it fails after 2 attempts, save and report.`;

// =============================================================================
// VALIDATORS
// =============================================================================

const REQUIRED_PATTERNS = {
  "@dataclass": "uses @dataclass decorator",
  "def greet": "defines greet function",
  "-> str": "uses return type hint",
};

export function createValidators() {
  return [
    new SkillInvokedValidator("python-patterns", { required: false }),
    new PythonFileValidator("user_greeting.py", {
      label: "User Greeting Script",
      required: REQUIRED_PATTERNS,
      requireAll: true,
      runFile: true,
    }),
    new MetricsCollector(["user_greeting.py"]),
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
    description: "With python-patterns skill",
    skills: {
      "python-patterns": [SKILL_CONTENT],
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
