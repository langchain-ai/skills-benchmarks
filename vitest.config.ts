/**
 * Vitest configuration for skill benchmarks.
 *
 * Supports parallel test execution like pytest-xdist.
 */

import { defineConfig } from "vitest/config";
import { resolve } from "node:path";

export default defineConfig({
  test: {
    // Test file patterns
    include: ["tests/**/*.test.ts"],

    // Global timeout (10 minutes per test)
    testTimeout: 600000,

    // Parallel execution configuration
    pool: "threads",
    poolOptions: {
      threads: {
        // Number of parallel workers (like pytest-xdist -n)
        minThreads: 1,
        maxThreads: 3,
      },
    },

    // Retry failed tests once
    retry: 0,

    // Reporter configuration
    reporters: ["verbose"],

    // Global setup (runs once before all tests)
    globalSetup: ["./tests/globalSetup.ts"],
  },
  resolve: {
    alias: {
      "@skills-benchmark/scaffold": resolve(__dirname, "scaffold/typescript/index.ts"),
    },
  },
});
