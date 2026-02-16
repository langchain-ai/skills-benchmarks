/**
 * Real LangSmith API data fixtures for testing.
 *
 * This data was captured from real LangSmith API responses to ensure
 * our mocks accurately reflect actual API behavior.
 *
 * Data captured on 2026-02-16 from project "skills".
 *
 * IMPORTANT: This data MUST match fixtures.py exactly for parity testing.
 */

import { writeFileSync } from "node:fs";
import { join } from "node:path";

// ============================================================================
// TRACE DATA - Captured from real API responses
// ============================================================================

/** Sample trace list output (from `traces list --limit 3 --format json`) */
export const SAMPLE_TRACES_LIST = [
  {
    run_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
    trace_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
    name: "LangGraph",
    run_type: "chain",
    parent_run_id: null,
    start_time: "2026-02-15T19:16:43.144899",
    end_time: "2026-02-15T19:16:46.686558",
  },
  {
    run_id: "019c62bb-92cc-71b0-97e7-8e2b283a432c",
    trace_id: "019c62bb-92cc-71b0-97e7-8e2b283a432c",
    name: "LangGraph",
    run_type: "chain",
    parent_run_id: null,
    start_time: "2026-02-15T19:16:25.932649",
    end_time: "2026-02-15T19:16:29.558129",
  },
  {
    run_id: "019c62bb-695f-70e2-a62a-e8fec7118137",
    trace_id: "019c62bb-695f-70e2-a62a-e8fec7118137",
    name: "LangGraph",
    run_type: "chain",
    parent_run_id: null,
    start_time: "2026-02-15T19:16:15.327190",
    end_time: "2026-02-15T19:16:15.554152",
  },
];

/** Full trace hierarchy (from `traces get <trace-id> --format json`) */
export const SAMPLE_TRACE_GET = {
  trace_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
  run_count: 7,
  runs: [
    {
      run_id: "019c62bb-de6a-7f61-a2a4-97366b55cc8d",
      trace_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      name: "ChatAnthropic",
      run_type: "llm",
      parent_run_id: "019c62bb-de69-7120-9c06-4e570c78062f",
      start_time: "2026-02-15T19:16:45.290780",
      end_time: "2026-02-15T19:16:46.683732",
    },
    {
      run_id: "019c62bb-de69-7120-9c06-4e570c78062f",
      trace_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      name: "model",
      run_type: "chain",
      parent_run_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      start_time: "2026-02-15T19:16:45.289146",
      end_time: "2026-02-15T19:16:46.685606",
    },
    {
      run_id: "019c62bb-de67-76a1-aabf-136119aa18a6",
      trace_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      name: "calculator",
      run_type: "tool",
      parent_run_id: "019c62bb-de66-7fe1-92e0-d45d12b5bf69",
      start_time: "2026-02-15T19:16:45.287767",
      end_time: "2026-02-15T19:16:45.288323",
    },
    {
      run_id: "019c62bb-de66-7fe1-92e0-d45d12b5bf69",
      trace_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      name: "tools",
      run_type: "chain",
      parent_run_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      start_time: "2026-02-15T19:16:45.286820",
      end_time: "2026-02-15T19:16:45.288848",
    },
    {
      run_id: "019c62bb-d650-7a42-be20-fd0b7e97ccc2",
      trace_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      name: "ChatAnthropic",
      run_type: "llm",
      parent_run_id: "019c62bb-d60c-78e0-acdc-0bd71a1bf4d0",
      start_time: "2026-02-15T19:16:43.216157",
      end_time: "2026-02-15T19:16:45.284788",
    },
    {
      run_id: "019c62bb-d60c-78e0-acdc-0bd71a1bf4d0",
      trace_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      name: "model",
      run_type: "chain",
      parent_run_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      start_time: "2026-02-15T19:16:43.148540",
      end_time: "2026-02-15T19:16:45.286248",
    },
    {
      run_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      trace_id: "019c62bb-d608-74c3-88bd-54d51db3d4a7",
      name: "LangGraph",
      run_type: "chain",
      parent_run_id: null,
      start_time: "2026-02-15T19:16:43.144899",
      end_time: "2026-02-15T19:16:46.686558",
    },
  ],
};

// ============================================================================
// DATASET DATA - Captured from real API responses
// ============================================================================

/** Sample datasets list (from `list-datasets`) */
export const SAMPLE_DATASETS = [
  {
    id: "7951866e-3433-49xx-xxxx-xxxxxxxxxxxx",
    name: "shipping-support-golden",
    description: "Test queries exposing context confusion patterns w",
    example_count: 10,
  },
  {
    id: "29b5bdde-60d7-41xx-xxxx-xxxxxxxxxxxx",
    name: "Email Agent Notebook: Trajectory",
    description: "",
    example_count: 5,
  },
  {
    id: "13fc661f-2a09-4axx-xxxx-xxxxxxxxxxxx",
    name: "Email Agent: Trajectory",
    description: "",
    example_count: 16,
  },
  {
    id: "d448c458-c63e-47xx-xxxx-xxxxxxxxxxxx",
    name: "kb-agent-golden-set",
    description: "Golden dataset for KB retrieval agent evaluation w",
    example_count: 15,
  },
];

/** Sample dataset examples (from `show "Email Agent: Trajectory"`) */
export const SAMPLE_DATASET_EXAMPLES = [
  {
    inputs: {
      email_input: {
        to: "Robert Xu <Robert@company.com>",
        author: "Marketing Team <marketing@openai.com>",
        subject: "Newsletter: New Model from OpenAI",
        email_thread: "Hi Robert,\n\nWe're excited to announce...",
      },
    },
    outputs: { trajectory: [] as string[] },
  },
  {
    inputs: {
      email_input: {
        to: "Robert Xu <Robert@company.com>",
        author: "Project Team <project@company.com>",
        subject: "Joint presentation next month",
        email_thread: "Hi Robert,\n\nThe leadership team has asked us...",
      },
    },
    outputs: {
      trajectory: [
        "check_calendar_availability",
        "schedule_meeting",
        "write_email",
        "done",
      ],
    },
  },
];

// ============================================================================
// LOCAL FILE FIXTURES - Sample data for testing without API
// ============================================================================

/** Sample trace runs in JSONL format (for generate_datasets testing) */
export const SAMPLE_TRACE_RUNS = [
  {
    run_id: "run-001",
    trace_id: "trace-001",
    name: "agent",
    run_type: "chain",
    parent_run_id: null,
    start_time: "2025-01-15T10:00:00Z",
    end_time: "2025-01-15T10:00:05Z",
    inputs: { query: "What is the capital of France?" },
    outputs: { answer: "Paris" },
  },
  {
    run_id: "run-002",
    trace_id: "trace-001",
    name: "search_tool",
    run_type: "tool",
    parent_run_id: "run-001",
    start_time: "2025-01-15T10:00:01Z",
    end_time: "2025-01-15T10:00:02Z",
    inputs: { query: "capital France" },
    outputs: { result: "Paris is the capital" },
  },
  {
    run_id: "run-003",
    trace_id: "trace-001",
    name: "llm",
    run_type: "llm",
    parent_run_id: "run-001",
    start_time: "2025-01-15T10:00:03Z",
    end_time: "2025-01-15T10:00:04Z",
    inputs: { messages: [{ role: "user", content: "summarize" }] },
    outputs: { answer: "Paris" },
  },
];

/** Sample dataset for query_datasets testing */
export const SAMPLE_LOCAL_DATASET = [
  {
    trace_id: "trace-001",
    inputs: { query: "What is the capital of France?" },
    outputs: { expected_response: "Paris" },
  },
  {
    trace_id: "trace-002",
    inputs: { query: "What is 2 + 2?" },
    outputs: { expected_response: "4" },
  },
];

// ============================================================================
// HELPER FUNCTIONS - Create test files from fixtures
// ============================================================================

/**
 * Create a sample JSONL trace file for testing.
 *
 * @param tmpPath - Directory to create the file in
 * @returns Path to the created JSONL file
 */
export function createSampleTraceJsonl(tmpPath: string): string {
  const jsonlFile = join(tmpPath, "trace-001.jsonl");
  const content = SAMPLE_TRACE_RUNS.map((r) => JSON.stringify(r)).join("\n");
  writeFileSync(jsonlFile, content);
  return jsonlFile;
}

/**
 * Create a sample dataset JSON file for testing.
 *
 * @param tmpPath - Directory to create the file in
 * @returns Path to the created JSON file
 */
export function createSampleDatasetJson(tmpPath: string): string {
  const jsonFile = join(tmpPath, "dataset.json");
  writeFileSync(jsonFile, JSON.stringify(SAMPLE_LOCAL_DATASET, null, 2));
  return jsonFile;
}
