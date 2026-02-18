/**
 * Docker-based code execution validation.
 *
 * Validators for running code in Docker and checking output.
 * Mirrors scaffold/python/validation/docker.py.
 */

import { existsSync } from "node:fs";
import { join } from "node:path";
import { runNodeInDocker, runPythonInDocker } from "../utils.js";
import type { ValidationResult } from "./core.js";

/**
 * Run a file in Docker and check output.
 */
export async function validateCodeExecution(
  testDir: string,
  filename: string,
  options: {
    label?: string;
    language?: "python" | "typescript";
    timeout?: number;
    expectedPatterns?: string[];
    forbiddenPatterns?: string[];
    minOutputLines?: number;
  } = {},
): Promise<ValidationResult> {
  const passed: string[] = [];
  const failed: string[] = [];
  const label = options.label || filename;
  const lang = options.language || (filename.endsWith(".py") ? "python" : "typescript");

  const filepath = join(testDir, filename);
  if (!existsSync(filepath)) {
    return { passed: [], failed: [`${label}: file not found`] };
  }

  // Run in Docker
  let success: boolean;
  let output: string;

  if (lang === "python") {
    [success, output] = runPythonInDocker(testDir, filename, {
      timeout: options.timeout,
    });
  } else {
    [success, output] = runNodeInDocker(testDir, filename, {
      timeout: options.timeout,
    });
  }

  if (!success) {
    return {
      passed: [],
      failed: [`${label}: execution failed - ${output.slice(0, 150)}`],
    };
  }

  passed.push(`${label}: runs successfully`);

  // Check minimum output lines
  if (options.minOutputLines) {
    const lines = output.trim().split("\n").filter((l) => l.trim()).length;
    if (lines < options.minOutputLines) {
      failed.push(`${label}: only ${lines} lines (need ${options.minOutputLines})`);
    } else {
      passed.push(`${label}: ${lines} lines output`);
    }
  }

  // Check expected patterns
  const outputLower = output.toLowerCase();
  for (const pattern of options.expectedPatterns || []) {
    if (outputLower.includes(pattern.toLowerCase())) {
      passed.push(`${label}: output contains "${pattern}"`);
    } else {
      failed.push(`${label}: output missing "${pattern}"`);
    }
  }

  // Check forbidden patterns
  for (const pattern of options.forbiddenPatterns || []) {
    if (outputLower.includes(pattern.toLowerCase())) {
      failed.push(`${label}: output contains forbidden "${pattern}"`);
    }
  }

  return { passed, failed };
}

/**
 * Run a Python file in Docker and validate output.
 */
export async function validatePythonExecution(
  testDir: string,
  filename: string,
  options: {
    label?: string;
    timeout?: number;
    expectedPatterns?: string[];
    minOutputLines?: number;
  } = {},
): Promise<ValidationResult> {
  return validateCodeExecution(testDir, filename, {
    ...options,
    language: "python",
  });
}

/**
 * Run a TypeScript file in Docker and validate output.
 */
export async function validateTypescriptExecution(
  testDir: string,
  filename: string,
  options: {
    label?: string;
    timeout?: number;
    expectedPatterns?: string[];
    minOutputLines?: number;
  } = {},
): Promise<ValidationResult> {
  return validateCodeExecution(testDir, filename, {
    ...options,
    language: "typescript",
  });
}
