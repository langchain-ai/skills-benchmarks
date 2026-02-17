#!/usr/bin/env npx tsx
/**
 * Evaluator test runner for Docker. Handles both exported and non-exported functions.
 * Usage: npx tsx eval_runner.ts <module_path> <func_name> <test_cases.json>
 */

import * as fs from "fs";
import * as path from "path";
import { pathToFileURL } from "url";

interface TestCase {
  name: string;
  run: Record<string, unknown>;
  example: Record<string, unknown>;
  expected_result: {
    should_not_crash?: boolean;
    min_score?: number;
    max_score?: number;
  };
}

function normalizeScore(score: unknown): number {
  if (typeof score === "boolean") return score ? 1 : 0;
  if (typeof score === "number") return score >= 0 && score <= 1 ? score : score > 1 ? score / 100 : 0;
  return 0;
}

function extractScore(result: unknown): number | null {
  if (typeof result === "number") return result;
  if (typeof result === "boolean") return result ? 1 : 0;
  if (result && typeof result === "object") {
    const obj = result as Record<string, unknown>;
    // Try standard keys first
    for (const key of ["score", "value", "result", "pass", "passed"]) {
      const val = obj[key];
      if (typeof val === "number") return val;
      if (typeof val === "boolean") return val ? 1 : 0;
    }
    // Fallback: find first numeric value (for custom metric keys like response_quality)
    for (const val of Object.values(obj)) {
      if (typeof val === "number") return val;
      if (typeof val === "boolean") return val ? 1 : 0;
    }
  }
  return null;
}

function functionExistsInFile(content: string, name: string): boolean {
  // Check for common function declaration patterns without extracting full source
  const patterns = [
    new RegExp(`(?:export\\s+)?(?:async\\s+)?function\\s+${name}\\s*\\(`),
    new RegExp(`(?:export\\s+)?const\\s+${name}\\s*=`),
  ];
  return patterns.some((p) => p.test(content));
}

async function runTestCase(
  evalFunc: (run: unknown, example: unknown) => unknown,
  tc: TestCase
): Promise<{ name: string; passed: boolean; score?: number; error?: string }> {
  const { name = "unknown", expected_result: expected = {} } = tc;
  try {
    const result = await evalFunc(tc.run || {}, tc.example || {});
    if (expected.should_not_crash) return { name, passed: true };

    const score = extractScore(result);
    if (score === null) return { name, passed: false, error: "no score" };

    const normalized = normalizeScore(score);
    const passed = normalized >= (expected.min_score ?? 0) && normalized <= (expected.max_score ?? 1);
    return { name, passed, score: normalized };
  } catch (e) {
    return { name, passed: false, error: String(e).slice(0, 50) };
  }
}

async function loadEvaluator(filePath: string, funcName: string) {
  const resolvedPath = path.resolve(filePath);
  const fileUrl = pathToFileURL(resolvedPath).href;

  // Try direct import (works for exported functions)
  try {
    const mod = await import(fileUrl);
    const fn = mod[funcName] || mod.default?.[funcName] || mod.default;
    if (typeof fn === "function") return fn;
  } catch {
    /* function may not be exported, try wrapper approach */
  }

  // Check if function exists before creating wrapper
  const content = fs.readFileSync(resolvedPath, "utf8");
  if (!functionExistsInFile(content, funcName)) return null;

  // Create wrapper: copy entire file and add export statement
  // This preserves all imports, type definitions, and dependencies
  const wrapperPath = resolvedPath.replace(/\.[jt]s$/, "_wrapper.mts");
  fs.writeFileSync(wrapperPath, content + `\nexport { ${funcName} };\n`);

  try {
    const mod = await import(pathToFileURL(wrapperPath).href);
    return mod[funcName] || mod.default;
  } finally {
    try {
      fs.unlinkSync(wrapperPath);
    } catch {
      /* cleanup failure is non-fatal */
    }
  }
}

async function main() {
  const [, , modulePath, funcName, testCasesFile] = process.argv;
  if (!modulePath || !funcName || !testCasesFile) {
    console.error("Usage: npx tsx eval_runner.ts <module_path> <func_name> <test_cases.json>");
    process.exit(1);
  }

  const resolvedPath = path.resolve(process.cwd(), modulePath);
  const evalFunc = await loadEvaluator(resolvedPath, funcName);

  if (typeof evalFunc !== "function") {
    console.error(`Function '${funcName}' not found in module`);
    process.exit(1);
  }

  const testCases: TestCase[] = JSON.parse(fs.readFileSync(testCasesFile, "utf8"));
  const results = await Promise.all(testCases.map((tc) => runTestCase(evalFunc, tc)));
  console.log("EVALUATOR_RESULTS:" + JSON.stringify(results));
}

main().catch((e) => {
  console.error("Error:", e);
  process.exit(1);
});
