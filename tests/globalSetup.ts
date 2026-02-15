/**
 * Global setup for Vitest - runs once before all tests.
 *
 * Verifies environment (Docker, Claude CLI, API keys).
 */

import { execSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { config as loadEnv } from "dotenv";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");
const SHELL_DIR = resolve(PROJECT_ROOT, "scaffold", "shell");

export default async function globalSetup(): Promise<void> {
  // Load .env file
  loadEnv({ path: resolve(PROJECT_ROOT, ".env") });

  const errors: string[] = [];

  // Check Docker
  try {
    execSync(`bash ${SHELL_DIR}/docker.sh check`, { stdio: "pipe" });
  } catch {
    errors.push("Docker not available or not running");
  }

  // Check Claude CLI
  try {
    execSync("claude --version", { stdio: "pipe" });
  } catch {
    errors.push("Claude CLI not available. Install from: https://claude.ai/code");
  }

  // Check API keys
  if (!process.env.ANTHROPIC_API_KEY) {
    errors.push("ANTHROPIC_API_KEY not set");
  }
  if (!process.env.OPENAI_API_KEY) {
    errors.push("OPENAI_API_KEY not set");
  }

  if (errors.length > 0) {
    console.error("\n=== Environment Verification Failed ===");
    for (const error of errors) {
      console.error(`  - ${error}`);
    }
    console.error("========================================\n");
    throw new Error(`Environment verification failed:\n${errors.join("\n")}`);
  }

  console.log("\n=== Environment Verified ===");
  console.log("  - Docker: OK");
  console.log("  - Claude CLI: OK");
  console.log("  - API Keys: OK");
  console.log("============================\n");
}
