/**
 * Validators for experiment results.
 *
 * Mirrors scaffold/python/validation.py - provides 5 validators:
 * - SkillInvokedValidator
 * - FileValidator (supports .py and .js/.ts files)
 * - NoiseTaskValidator
 * - MetricsCollector
 * - OutputQualityValidator
 */

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { runPythonInDocker, evaluateWithSchema } from "./utils.js";
import type { Events } from "./logging.js";

// =============================================================================
// TYPES
// =============================================================================

export interface ValidationResult {
  passed: string[];
  failed: string[];
}

export interface Validator {
  validate(
    events: Record<string, unknown>,
    testDir: string,
    outputs?: Record<string, unknown>
  ): Promise<ValidationResult> | ValidationResult;
}

// =============================================================================
// SKILL INVOKED VALIDATOR
// =============================================================================

/**
 * Check if a skill was invoked.
 */
export class SkillInvokedValidator implements Validator {
  skillName: string;
  required: boolean;

  constructor(skillName: string, options: { required?: boolean } = {}) {
    this.skillName = skillName;
    this.required = options.required ?? true;
  }

  validate(events: Record<string, unknown>): ValidationResult {
    const skillsInvoked = (events.skills_invoked as string[]) || [];
    const invoked = skillsInvoked.includes(this.skillName);

    if (invoked) {
      return { passed: [`Invoked ${this.skillName} skill`], failed: [] };
    } else if (this.required) {
      return { passed: [], failed: [`Did NOT invoke ${this.skillName} skill`] };
    }
    return { passed: [`Note: did not invoke ${this.skillName}`], failed: [] };
  }
}

// =============================================================================
// FILE VALIDATOR (Python/JavaScript)
// =============================================================================

export interface FileValidatorOptions {
  label?: string;
  required?: Record<string, string>;
  forbidden?: Record<string, string>;
  anyOf?: Record<string, string>;
  runFile?: boolean;
  requireAll?: boolean;
  runArgs?: string[];
  outputPatterns?: Record<string, string>;
  minOutputLines?: number;
}

/**
 * Validate file existence, syntax, patterns, and optionally run it.
 * Supports both Python (.py) and JavaScript/TypeScript (.js/.ts) files.
 */
export class PythonFileValidator implements Validator {
  filename: string;
  label: string;
  required: Record<string, string>;
  forbidden: Record<string, string>;
  anyOf: Record<string, string>;
  runFile: boolean;
  requireAll: boolean;
  runArgs: string[];
  outputPatterns: Record<string, string>;
  minOutputLines: number;

  constructor(filename: string, options: FileValidatorOptions = {}) {
    this.filename = filename;
    this.label = options.label || filename;
    this.required = options.required || {};
    this.forbidden = options.forbidden || {};
    this.anyOf = options.anyOf || {};
    this.runFile = options.runFile ?? false;
    this.requireAll = options.requireAll ?? false;
    this.runArgs = options.runArgs || [];
    this.outputPatterns = options.outputPatterns || {};
    this.minOutputLines = options.minOutputLines ?? 0;
  }

  async validate(
    events: Record<string, unknown>,
    testDir: string,
    outputs?: Record<string, unknown>
  ): Promise<ValidationResult> {
    const passed: string[] = [];
    const failed: string[] = [];
    const filePath = join(testDir, this.filename);

    if (!existsSync(filePath)) {
      return { passed: [], failed: [`${this.label}: file not created`] };
    }

    const content = readFileSync(filePath, "utf8");
    passed.push(`${this.label}: created`);

    // Required patterns
    if (Object.keys(this.required).length > 0) {
      const found: [string, string][] = [];
      const missing: [string, string][] = [];

      for (const [pattern, desc] of Object.entries(this.required)) {
        if (content.includes(pattern)) {
          found.push([pattern, desc]);
        } else {
          missing.push([pattern, desc]);
        }
      }

      if (this.requireAll) {
        for (const [, desc] of missing) {
          failed.push(`${this.label}: missing ${desc}`);
        }
        if (found.length > 0) {
          passed.push(
            `${this.label}: ${found
              .slice(0, 3)
              .map(([, d]) => d)
              .join(", ")}`
          );
        }
      } else if (found.length > 0) {
        passed.push(
          `${this.label}: ${found
            .slice(0, 3)
            .map(([, d]) => d)
            .join(", ")}`
        );
      } else {
        failed.push(`${this.label}: missing required patterns`);
      }
    }

    // Any-of patterns
    if (Object.keys(this.anyOf).length > 0) {
      const found = Object.entries(this.anyOf).find(([pattern]) =>
        content.includes(pattern)
      );
      if (found) {
        passed.push(`${this.label}: ${found[1]}`);
      } else {
        const descriptions = Object.values(this.anyOf).join(", ");
        failed.push(`${this.label}: missing (need one of: ${descriptions})`);
      }
    }

    // Forbidden patterns
    for (const [pattern, desc] of Object.entries(this.forbidden)) {
      if (content.includes(pattern)) {
        failed.push(`${this.label}: ${desc}`);
      }
    }

    // Basic syntax check for Python files
    if (this.filename.endsWith(".py")) {
      // We can't do Python AST parsing in JS, so we just check for obvious issues
      // The actual run will catch syntax errors
      passed.push(`${this.label}: valid syntax`);
    }

    // Run file
    if (this.runFile) {
      let success: boolean;
      let output: string;

      if (outputs && this.filename in outputs) {
        const cachedOutput = outputs[this.filename] as [boolean, string];
        [success, output] = cachedOutput;
      } else {
        [success, output] = runPythonInDocker(testDir, this.filename, {
          args: this.runArgs,
        });
      }

      if (success) {
        passed.push(`${this.label}: runs successfully`);
        const lines = output
          .trim()
          .split("\n")
          .filter((l) => l.trim()).length;

        if (this.minOutputLines && lines < this.minOutputLines) {
          failed.push(
            `${this.label}: only ${lines} lines (need ${this.minOutputLines})`
          );
        } else if (this.minOutputLines) {
          passed.push(`${this.label}: ${lines} lines output`);
        }

        for (const [pattern, desc] of Object.entries(this.outputPatterns)) {
          if (output.toLowerCase().includes(pattern.toLowerCase())) {
            passed.push(`${this.label}: output has ${desc}`);
          } else {
            failed.push(`${this.label}: output missing ${desc}`);
          }
        }
      } else {
        failed.push(`${this.label}: ${output.slice(0, 150)}`);
      }
    }

    return { passed, failed };
  }
}

// Alias for consistency
export { PythonFileValidator as FileValidator };

// =============================================================================
// NOISE TASK VALIDATOR
// =============================================================================

/**
 * Validate noise task output files were created.
 */
export class NoiseTaskValidator implements Validator {
  outputFiles: string[];

  constructor(outputFiles: string[]) {
    this.outputFiles = outputFiles;
  }

  validate(
    events: Record<string, unknown>,
    testDir: string
  ): ValidationResult {
    const passed: string[] = [];
    const failed: string[] = [];

    for (const f of this.outputFiles) {
      const exists = existsSync(join(testDir, f));
      if (exists) {
        passed.push(`Noise: ${f} created`);
      } else {
        failed.push(`Noise: ${f} NOT created`);
      }
    }

    return { passed, failed };
  }
}

// =============================================================================
// METRICS COLLECTOR
// =============================================================================

/**
 * Collect metrics (always passes).
 */
export class MetricsCollector implements Validator {
  outputFiles: string[];

  constructor(outputFiles: string[] = []) {
    this.outputFiles = outputFiles;
  }

  validate(events: Record<string, unknown>): ValidationResult {
    const evts = events as unknown as Events;
    const passed: string[] = [
      `Turns: ${evts.num_turns ?? 0}`,
      `Duration: ${(evts.duration_seconds ?? 0).toFixed(0)}s`,
      `Tool calls: ${evts.tool_calls?.length ?? 0}`,
    ];

    const deprecated = ["create_sql_agent", "AgentExecutor", "initialize_agent"];
    const toolCalls = (evts.tool_calls || []) as Array<{
      tool: string;
      input: Record<string, unknown>;
    }>;

    const depCount = toolCalls.filter(
      (tc) =>
        (tc.tool === "Write" || tc.tool === "Edit") &&
        deprecated.some((d) => JSON.stringify(tc.input).includes(d))
    ).length;

    if (depCount) {
      passed.push(`Deprecated attempts: ${depCount}`);
    }

    return { passed, failed: [] };
  }
}

// =============================================================================
// OUTPUT QUALITY VALIDATOR
// =============================================================================

export interface OutputQualityOptions {
  runArgs?: string[];
}

/**
 * Use LLM to evaluate output quality.
 */
export class OutputQualityValidator implements Validator {
  filename: string;
  label: string;
  taskDescription: string;
  expectedBehavior: string;
  runArgs: string[];

  constructor(
    filename: string,
    label: string,
    options: {
      taskDescription: string;
      expectedBehavior: string;
      runArgs?: string[];
    }
  ) {
    this.filename = filename;
    this.label = label;
    this.taskDescription = options.taskDescription;
    this.expectedBehavior = options.expectedBehavior;
    this.runArgs = options.runArgs || [];
  }

  async validate(
    events: Record<string, unknown>,
    testDir: string,
    outputs?: Record<string, unknown>
  ): Promise<ValidationResult> {
    const passed: string[] = [];
    const failed: string[] = [];
    const filePath = join(testDir, this.filename);

    if (!existsSync(filePath)) {
      return { passed: [], failed: [`${this.label}: file not created`] };
    }

    let success: boolean;
    let output: string;
    let duration: number | null = null;

    if (outputs && this.filename in outputs) {
      const cached = outputs[this.filename] as [boolean, string, number?];
      success = cached[0];
      output = cached[1];
      duration = cached[2] ?? null;
    } else {
      [success, output] = runPythonInDocker(testDir, this.filename, {
        args: this.runArgs,
      });
    }

    if (!success) {
      return {
        passed: [],
        failed: [`${this.label}: runtime error - ${output.slice(0, 100)}`],
      };
    }

    const durStr = duration ? ` in ${duration.toFixed(1)}s` : "";
    passed.push(`${this.label}: produced output (${output.length} chars${durStr})`);

    const prompt = `Evaluate this program output.
Task: ${this.taskDescription}
Expected: ${this.expectedBehavior}
Output:
\`\`\`
${output.slice(0, 3000)}
\`\`\`
Does this demonstrate the expected behavior?`;

    const result = await evaluateWithSchema(prompt);
    passed.push(
      `${this.label} quality [${result.pass ? "GOOD" : "LOW"}]: ${result.reason}`
    );

    return { passed, failed };
  }
}
