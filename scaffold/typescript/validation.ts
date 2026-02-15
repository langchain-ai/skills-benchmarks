/**
 * Validators for experiment results.
 */

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { runNodeInDocker, evaluateWithSchema } from "./utils.js";
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

export class SkillInvokedValidator implements Validator {
  constructor(
    public skillName: string,
    public options: { required?: boolean } = {}
  ) {}

  validate(events: Record<string, unknown>): ValidationResult {
    const skillsInvoked = (events.skills_invoked as string[]) || [];
    const invoked = skillsInvoked.includes(this.skillName);
    const required = this.options.required ?? true;

    if (invoked) return { passed: [`Invoked ${this.skillName} skill`], failed: [] };
    if (required) return { passed: [], failed: [`Did NOT invoke ${this.skillName} skill`] };
    return { passed: [`Note: did not invoke ${this.skillName}`], failed: [] };
  }
}

// =============================================================================
// FILE VALIDATOR
// =============================================================================

export interface FileValidatorOptions {
  label?: string;
  required?: Record<string, string>; // pattern -> description
  forbidden?: Record<string, string>;
  anyOf?: Record<string, string>;
  runFile?: boolean;
  requireAll?: boolean;
  runArgs?: string[];
  outputPatterns?: Record<string, string>;
  minOutputLines?: number;
}

/** Validate TypeScript/JavaScript file existence, patterns, and optionally run it. */
export class TypeScriptFileValidator implements Validator {
  constructor(
    public filename: string,
    public opts: FileValidatorOptions = {}
  ) {}

  async validate(
    _events: Record<string, unknown>,
    testDir: string,
    outputs?: Record<string, unknown>
  ): Promise<ValidationResult> {
    const passed: string[] = [];
    const failed: string[] = [];
    const label = this.opts.label || this.filename;
    const filePath = join(testDir, this.filename);

    if (!existsSync(filePath)) {
      return { passed: [], failed: [`${label}: file not created`] };
    }
    passed.push(`${label}: created`);

    const content = readFileSync(filePath, "utf8");

    // Check required patterns
    const required = this.opts.required || {};
    if (Object.keys(required).length > 0) {
      const found = Object.entries(required).filter(([p]) => content.includes(p));
      const missing = Object.entries(required).filter(([p]) => !content.includes(p));

      if (this.opts.requireAll) {
        missing.forEach(([, d]) => failed.push(`${label}: missing ${d}`));
        if (found.length) passed.push(`${label}: ${found.slice(0, 3).map(([, d]) => d).join(", ")}`);
      } else if (found.length) {
        passed.push(`${label}: ${found.slice(0, 3).map(([, d]) => d).join(", ")}`);
      } else {
        failed.push(`${label}: missing required patterns`);
      }
    }

    // Check any-of patterns
    const anyOf = this.opts.anyOf || {};
    if (Object.keys(anyOf).length > 0) {
      const found = Object.entries(anyOf).find(([p]) => content.includes(p));
      if (found) {
        passed.push(`${label}: ${found[1]}`);
      } else {
        failed.push(`${label}: missing (need one of: ${Object.values(anyOf).join(", ")})`);
      }
    }

    // Check forbidden patterns
    for (const [pattern, desc] of Object.entries(this.opts.forbidden || {})) {
      if (content.includes(pattern)) failed.push(`${label}: ${desc}`);
    }

    // Run file if requested
    if (this.opts.runFile) {
      let success: boolean, output: string;
      if (outputs && this.filename in outputs) {
        [success, output] = outputs[this.filename] as [boolean, string];
      } else {
        [success, output] = runNodeInDocker(testDir, this.filename, { args: this.opts.runArgs || [] });
      }

      if (success) {
        passed.push(`${label}: runs successfully`);
        const lines = output.trim().split("\n").filter((l) => l.trim()).length;

        if (this.opts.minOutputLines && lines < this.opts.minOutputLines) {
          failed.push(`${label}: only ${lines} lines (need ${this.opts.minOutputLines})`);
        } else if (this.opts.minOutputLines) {
          passed.push(`${label}: ${lines} lines output`);
        }

        for (const [pattern, desc] of Object.entries(this.opts.outputPatterns || {})) {
          if (output.toLowerCase().includes(pattern.toLowerCase())) {
            passed.push(`${label}: output has ${desc}`);
          } else {
            failed.push(`${label}: output missing ${desc}`);
          }
        }
      } else {
        failed.push(`${label}: ${output.slice(0, 150)}`);
      }
    }

    return { passed, failed };
  }
}

export { TypeScriptFileValidator as FileValidator };

// =============================================================================
// NOISE TASK VALIDATOR
// =============================================================================

/** Validate noise task output files were created. */
export class NoiseTaskValidator implements Validator {
  constructor(public outputFiles: string[]) {}

  validate(_events: Record<string, unknown>, testDir: string): ValidationResult {
    const passed: string[] = [];
    const failed: string[] = [];
    for (const f of this.outputFiles) {
      if (existsSync(join(testDir, f))) passed.push(`Noise: ${f} created`);
      else failed.push(`Noise: ${f} NOT created`);
    }
    return { passed, failed };
  }
}

// =============================================================================
// METRICS COLLECTOR
// =============================================================================

/** Collect metrics (always passes). */
export class MetricsCollector implements Validator {
  constructor(public outputFiles: string[] = []) {}

  validate(events: Record<string, unknown>): ValidationResult {
    const evts = events as unknown as Events;
    const passed = [
      `Turns: ${evts.num_turns ?? 0}`,
      `Duration: ${(evts.duration_seconds ?? 0).toFixed(0)}s`,
      `Tool calls: ${evts.tool_calls?.length ?? 0}`,
    ];

    // Check for deprecated API usage attempts
    const deprecated = ["create_sql_agent", "AgentExecutor", "initialize_agent"];
    const toolCalls = (evts.tool_calls || []) as Array<{ tool: string; input: Record<string, unknown> }>;
    const depCount = toolCalls.filter(
      (tc) => (tc.tool === "Write" || tc.tool === "Edit") && deprecated.some((d) => JSON.stringify(tc.input).includes(d))
    ).length;
    if (depCount) passed.push(`Deprecated attempts: ${depCount}`);

    return { passed, failed: [] };
  }
}

// =============================================================================
// OUTPUT QUALITY VALIDATOR
// =============================================================================

export interface OutputQualityOptions {
  runArgs?: string[];
}

/** Use LLM to evaluate output quality. */
export class OutputQualityValidator implements Validator {
  constructor(
    public filename: string,
    public label: string,
    public opts: { taskDescription: string; expectedBehavior: string; runArgs?: string[] }
  ) {}

  async validate(
    _events: Record<string, unknown>,
    testDir: string,
    outputs?: Record<string, unknown>
  ): Promise<ValidationResult> {
    const passed: string[] = [];
    const filePath = join(testDir, this.filename);

    if (!existsSync(filePath)) {
      return { passed: [], failed: [`${this.label}: file not created`] };
    }

    // Get output (from cache or by running)
    let success: boolean, output: string, duration: number | null = null;
    if (outputs && this.filename in outputs) {
      const cached = outputs[this.filename] as [boolean, string, number?];
      [success, output, duration] = [cached[0], cached[1], cached[2] ?? null];
    } else {
      [success, output] = runNodeInDocker(testDir, this.filename, { args: this.opts.runArgs || [] });
    }

    if (!success) {
      return { passed: [], failed: [`${this.label}: runtime error - ${output.slice(0, 100)}`] };
    }

    const durStr = duration ? ` in ${duration.toFixed(1)}s` : "";
    passed.push(`${this.label}: produced output (${output.length} chars${durStr})`);

    // Evaluate with LLM
    const prompt = `Evaluate this program output.
Task: ${this.opts.taskDescription}
Expected: ${this.opts.expectedBehavior}
Output:
\`\`\`
${output.slice(0, 3000)}
\`\`\`
Does this demonstrate the expected behavior?`;

    const result = await evaluateWithSchema(prompt);
    passed.push(`${this.label} quality [${result.pass ? "GOOD" : "LOW"}]: ${result.reason}`);

    return { passed, failed: [] };
  }
}
