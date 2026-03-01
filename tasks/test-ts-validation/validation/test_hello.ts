/**
 * TypeScript validation script for test-ts-validation task.
 *
 * Tests that hello.ts exists, has correct exports, and works.
 * Outputs JSON {"passed": [...], "failed": [...]} for the framework.
 */

import { readFileSync, existsSync, writeFileSync } from "node:fs";
import { execSync } from "node:child_process";

const RUN_CONTEXT_FILE = process.env.BENCH_RUN_CONTEXT || "_test_context.json";
const TEST_RESULTS_FILE = process.env.BENCH_TEST_RESULTS || "_test_results.json";

const passed: string[] = [];
const failed: string[] = [];

// Load context
let context: Record<string, unknown> = {};
try {
  context = JSON.parse(readFileSync(RUN_CONTEXT_FILE, "utf8"));
} catch {
  console.error(`Error: ${RUN_CONTEXT_FILE} not found or empty`);
  process.exit(1);
}

const artifacts = (context.target_artifacts as string[]) || ["hello.ts"];

// Check 1: File exists
const filepath = artifacts[0];
if (existsSync(filepath)) {
  passed.push(`${filepath} exists`);
} else {
  failed.push(`${filepath} not found`);
}

// Check 2: Has greet export
if (existsSync(filepath)) {
  const source = readFileSync(filepath, "utf8");
  if (/export\s+(function\s+greet|const\s+greet|{[^}]*greet[^}]*})/.test(source)) {
    passed.push("greet function exported");
  } else {
    failed.push("greet function not exported");
  }

  // Check 3: Function takes name parameter
  if (/greet\s*\(\s*name\s*(:\s*string)?/.test(source)) {
    passed.push("greet takes name parameter");
  } else {
    failed.push("greet missing name parameter");
  }
}

// Check 4: Executes without error
if (existsSync(filepath)) {
  try {
    // Write a temp runner to avoid inline eval quoting issues
    const runner = "_run_hello.ts";
    writeFileSync(runner, `import { greet } from "./${filepath}";\nconsole.log(greet("World"));\n`);
    const output = execSync(`npx tsx ${runner}`, {
      encoding: "utf8",
      timeout: 10000,
    }).trim();
    if (output.includes("World")) {
      passed.push(`execution: output contains greeting ("${output}")`);
    } else {
      failed.push(`execution: unexpected output "${output}"`);
    }
  } catch (e) {
    failed.push(`execution: ${String(e).slice(0, 100)}`);
  }
}

// Output results
const results = { passed, failed, error: null };
console.log(JSON.stringify(results, null, 2));
writeFileSync(TEST_RESULTS_FILE, JSON.stringify(results, null, 2));
process.exit(failed.length > 0 ? 1 : 0);
