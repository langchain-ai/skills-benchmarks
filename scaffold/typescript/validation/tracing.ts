/**
 * LangSmith tracing validation.
 *
 * Validators for checking Python and TypeScript files have proper LangSmith tracing.
 * Mirrors scaffold/python/validation/tracing.py.
 */

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import type { ValidationResult } from "./core.js";

// =============================================================================
// PATTERN DEFINITIONS
// =============================================================================

/** Python LangSmith tracing patterns */
const PYTHON_TRACING_PATTERNS = {
  traceable_import: {
    pattern: /from\s+langsmith\s+import.*traceable/,
    description: "imports traceable from langsmith",
  },
  traceable_decorator: {
    pattern: /@traceable/,
    description: "uses @traceable decorator",
  },
  wrap_openai_import: {
    pattern: /from\s+langsmith\.wrappers\s+import.*wrap_openai/,
    description: "imports wrap_openai",
  },
  wrap_openai_usage: {
    pattern: /wrap_openai\s*\(/,
    description: "wraps OpenAI client",
  },
};

/** TypeScript LangSmith tracing patterns */
const TYPESCRIPT_TRACING_PATTERNS = {
  traceable_import: {
    pattern: /import\s*\{[^}]*traceable[^}]*\}\s*from\s*["']langsmith/,
    description: "imports traceable from langsmith",
  },
  traceable_usage: {
    pattern: /traceable\s*\(/,
    description: "uses traceable function",
  },
  wrap_openai_import: {
    pattern: /import\s*\{[^}]*wrapOpenAI[^}]*\}\s*from\s*["']langsmith/,
    description: "imports wrapOpenAI",
  },
  wrap_openai_usage: {
    pattern: /wrapOpenAI\s*\(/,
    description: "wraps OpenAI client",
  },
};

// =============================================================================
// VALIDATOR FUNCTIONS
// =============================================================================

/**
 * Validate Python file has LangSmith tracing patterns.
 */
export function checkPythonTracing(
  testDir: string,
  filename: string,
  options: {
    label?: string;
    requireAll?: boolean;
    patterns?: typeof PYTHON_TRACING_PATTERNS;
  } = {},
): ValidationResult {
  const passed: string[] = [];
  const failed: string[] = [];
  const label = options.label || `Python (${filename})`;
  const patterns = options.patterns || PYTHON_TRACING_PATTERNS;
  const requireAll = options.requireAll ?? true;

  const filepath = join(testDir, filename);
  if (!existsSync(filepath)) {
    return { passed: [], failed: [`${label}: file not found`] };
  }

  const content = readFileSync(filepath, "utf8");
  passed.push(`${label}: file exists`);

  // Check patterns
  const found: string[] = [];
  const missing: string[] = [];

  for (const [, { pattern, description }] of Object.entries(patterns)) {
    if (pattern.test(content)) {
      found.push(description);
    } else {
      missing.push(description);
    }
  }

  if (found.length > 0) {
    passed.push(`${label}: ${found.slice(0, 3).join(", ")}`);
  }

  if (requireAll && missing.length > 0) {
    failed.push(...missing.map((desc) => `${label}: missing ${desc}`));
  } else if (found.length === 0) {
    failed.push(`${label}: no tracing patterns found`);
  }

  return { passed, failed };
}

/**
 * Validate TypeScript file has LangSmith tracing patterns.
 */
export function checkTypescriptTracing(
  testDir: string,
  filename: string,
  options: {
    label?: string;
    requireAll?: boolean;
    patterns?: typeof TYPESCRIPT_TRACING_PATTERNS;
  } = {},
): ValidationResult {
  const passed: string[] = [];
  const failed: string[] = [];
  const label = options.label || `TypeScript (${filename})`;
  const patterns = options.patterns || TYPESCRIPT_TRACING_PATTERNS;
  const requireAll = options.requireAll ?? true;

  const filepath = join(testDir, filename);
  if (!existsSync(filepath)) {
    return { passed: [], failed: [`${label}: file not found`] };
  }

  const content = readFileSync(filepath, "utf8");
  passed.push(`${label}: file exists`);

  // Check patterns
  const found: string[] = [];
  const missing: string[] = [];

  for (const [, { pattern, description }] of Object.entries(patterns)) {
    if (pattern.test(content)) {
      found.push(description);
    } else {
      missing.push(description);
    }
  }

  if (found.length > 0) {
    passed.push(`${label}: ${found.slice(0, 3).join(", ")}`);
  }

  if (requireAll && missing.length > 0) {
    failed.push(...missing.map((desc) => `${label}: missing ${desc}`));
  } else if (found.length === 0) {
    failed.push(`${label}: no tracing patterns found`);
  }

  return { passed, failed };
}

/**
 * Validate file has valid language syntax (basic check).
 */
export function checkLanguageSyntax(
  testDir: string,
  filename: string,
  language: "python" | "typescript",
): ValidationResult {
  const filepath = join(testDir, filename);
  const label = language === "python" ? `Python (${filename})` : `TypeScript (${filename})`;

  if (!existsSync(filepath)) {
    return { passed: [], failed: [`${label}: file not found`] };
  }

  const content = readFileSync(filepath, "utf8");

  // Basic syntax checks
  if (language === "python") {
    // Check for Python-specific syntax markers
    const hasPythonSyntax =
      /\bdef\s+\w+\s*\(/.test(content) || // function definition
      /\bclass\s+\w+/.test(content) || // class definition
      /\bimport\s+\w+/.test(content) || // import statement
      /\bfrom\s+\w+\s+import/.test(content); // from import

    if (hasPythonSyntax) {
      return { passed: [`${label}: valid Python syntax`], failed: [] };
    }
    return { passed: [], failed: [`${label}: no Python syntax markers found`] };
  } else {
    // Check for TypeScript-specific syntax markers
    const hasTsSyntax =
      /\b(async\s+)?function\s+\w+/.test(content) || // function
      /\bconst\s+\w+\s*=/.test(content) || // const declaration
      /\bclass\s+\w+/.test(content) || // class
      /\bimport\s+\{/.test(content) || // import with braces
      /\bexport\s+(const|function|class|interface|type)/.test(content); // export

    if (hasTsSyntax) {
      return { passed: [`${label}: valid TypeScript syntax`], failed: [] };
    }
    return { passed: [], failed: [`${label}: no TypeScript syntax markers found`] };
  }
}
