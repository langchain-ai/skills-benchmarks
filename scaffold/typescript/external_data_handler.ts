/**
 * External data handlers for test setup and cleanup.
 *
 * Handlers manage external LangSmith resources during tests.
 * All resources use a namespace pattern: bench-{type}-{run_id}
 *
 * Available handlers:
 *   - upload_traces: Upload trace fixtures to a LangSmith project
 *   - upload_datasets: Upload dataset JSON files to LangSmith
 *   - cleanup_namespace: Delete all LangSmith resources ending with -{run_id}
 */

import { Client } from "langsmith";
import { v4 as uuidv4 } from "uuid";
import { existsSync, globSync, readFileSync } from "node:fs";
import { join, basename } from "node:path";
import type { DataHandler } from "./tasks.js";

/**
 * Glob files in a directory matching the pattern.
 * Wrapper around Node.js globSync with sorted results.
 */
function matchFiles(dir: string, pattern: string): string[] {
  if (!existsSync(dir)) return [];
  return globSync(join(dir, pattern)).sort();
}

// =============================================================================
// LANGSMITH CLIENT
// =============================================================================

function getLangsmithClient(): { client: Client | null; error: string | null } {
  try {
    const client = new Client();
    return { client, error: null };
  } catch (e) {
    return { client: null, error: String(e) };
  }
}

// =============================================================================
// HELPERS
// =============================================================================

function parseTimestamp(s: string | undefined): Date | null {
  if (!s) return null;
  try {
    return new Date(s.replace("Z", "+00:00"));
  } catch {
    return null;
  }
}

interface TraceOperation {
  id?: string;
  operation?: string;
  name?: string;
  run_type?: string;
  inputs?: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  start_time?: string;
  end_time?: string;
  parent_run_id?: string;
  extra?: Record<string, unknown>;
  tags?: string[];
  error?: string;
}

async function replayTraceOperations(
  client: Client,
  project: string,
  operations: TraceOperation[]
): Promise<string | null> {
  // Build ID mapping for all post operations
  const idMap: Record<string, string> = {};
  for (const op of operations) {
    if (op.operation === "post" && op.id) {
      idMap[op.id] = uuidv4();
    }
  }
  if (Object.keys(idMap).length === 0) return null;

  // Calculate time shift
  const timestamps = operations
    .filter((op) => op.operation === "post")
    .map((op) => parseTimestamp(op.start_time))
    .filter((t): t is Date => t !== null);

  if (timestamps.length === 0) return null;

  const minTime = Math.min(...timestamps.map((t) => t.getTime()));
  const offset = Date.now() - minTime - 5 * 60 * 1000; // 5 minutes ago

  function shiftTs(tsStr: string | undefined): Date | undefined {
    const ts = parseTimestamp(tsStr);
    return ts ? new Date(ts.getTime() + offset) : undefined;
  }

  let rootId: string | null = null;

  for (const op of operations) {
    const oldId = op.id;
    const newId = oldId ? idMap[oldId] || oldId : oldId;
    const newParent = op.parent_run_id ? idMap[op.parent_run_id] : undefined;

    if (op.operation === "post") {
      try {
        await client.createRun({
          id: newId,
          name: op.name || "unknown",
          run_type: op.run_type || "chain",
          inputs: op.inputs || {},
          start_time: shiftTs(op.start_time)?.toISOString(),
          parent_run_id: newParent,
          project_name: project,
          extra: { ...(op.extra || {}), tags: op.tags || [] },
        });
        if (!op.parent_run_id) {
          rootId = newId || null;
        }
      } catch (e) {
        console.log(`    Failed: ${op.name}: ${e}`);
      }
    } else if (op.operation === "patch") {
      try {
        await client.updateRun(newId!, {
          end_time: shiftTs(op.end_time)?.toISOString(),
          outputs: op.outputs || {},
          error: op.error,
        });
      } catch (e) {
        console.log(`    Failed patch: ${op.name}: ${e}`);
      }
    }
  }

  return rootId;
}

// =============================================================================
// HANDLERS
// =============================================================================

export interface HandlerArgs {
  project?: string;
  data_dir?: string;
  run_id?: string;
  [key: string]: unknown;
}

/**
 * Upload trace fixtures from jsonl files to LangSmith project.
 */
export async function uploadTraces(args: HandlerArgs): Promise<Record<string, string>> {
  const { client, error } = getLangsmithClient();
  if (error || !client) {
    console.log(`Could not upload traces: ${error}`);
    return {};
  }

  const dataDir = args.data_dir;
  if (!dataDir || !existsSync(dataDir)) {
    return {};
  }

  const project = args.project || "default";
  const idMapping: Record<string, string> = {};

  const jsonlFiles = matchFiles(dataDir, "trace_*.jsonl");
  for (const jsonlFile of jsonlFiles) {
    const content = readFileSync(jsonlFile, "utf8");
    const operations: TraceOperation[] = content
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line));

    if (operations.length === 0) continue;

    // Find root trace and extract query for logging
    const root = operations.find((op) => op.operation === "post" && !op.parent_run_id);
    const oldId = root?.id;
    const messages = (root?.inputs?.messages || []) as Array<{ content?: string }>;
    const query = messages[0]?.content?.slice(0, 40) || "";

    try {
      const newId = await replayTraceOperations(client, project, operations);
      if (newId && oldId) {
        idMapping[oldId] = newId;
        console.log(`  Uploaded: ${query}...`);
      }
    } catch (e) {
      console.log(`  Failed (${query}): ${e}`);
    }
  }

  return idMapping;
}

/**
 * Upload dataset JSON files to LangSmith using naming convention.
 * File naming: {type}_*_dataset.json → bench-{type}-{run_id}
 */
export async function uploadDatasets(args: HandlerArgs): Promise<Record<string, string>> {
  const { client, error } = getLangsmithClient();
  if (error || !client) {
    console.log(`Could not upload datasets: ${error}`);
    return {};
  }

  const dataDir = args.data_dir;
  const runId = args.run_id;
  if (!dataDir || !existsSync(dataDir) || !runId) {
    return {};
  }

  const created: Record<string, string> = {};
  const datasetFiles = matchFiles(dataDir, "*_dataset.json");

  for (const filePath of datasetFiles) {
    const fileName = basename(filePath);
    // Extract type from filename: sql_agent_trajectory_dataset.json → sql
    const fileType = fileName.split("_")[0];
    const datasetName = `bench-${fileType}-${runId}`;

    try {
      const content = readFileSync(filePath, "utf8");
      let examples = JSON.parse(content);
      if (!Array.isArray(examples)) {
        examples = [examples];
      }

      // Create dataset and add examples
      const dataset = await client.createDataset(datasetName);
      const inputs = examples.map((ex: Record<string, unknown>) => ex.inputs || {});
      const outputs = examples.map((ex: Record<string, unknown>) => ex.outputs || {});

      await client.createExamples({
        inputs,
        outputs,
        datasetId: dataset.id,
      });

      created[fileName] = datasetName;
      console.log(`  Uploaded ${examples.length} examples to ${datasetName}`);
    } catch (e) {
      console.log(`  Failed to upload ${fileName}: ${e}`);
    }
  }

  return created;
}

/**
 * Delete all evaluators attached to the given dataset IDs.
 */
async function deleteEvaluatorsForDatasets(datasetIds: Set<string>): Promise<string[]> {
  if (datasetIds.size === 0) return [];

  const apiKey = process.env.LANGSMITH_API_KEY;
  const apiUrl = process.env.LANGSMITH_API_URL || "https://api.smith.langchain.com";

  if (!apiKey) return [];

  const deleted: string[] = [];

  try {
    const response = await fetch(`${apiUrl}/runs/rules`, {
      headers: { "x-api-key": apiKey },
    });

    if (!response.ok) return [];

    const rules = (await response.json()) as Array<{
      id: string;
      display_name?: string;
      dataset_id?: string;
    }>;

    for (const rule of rules) {
      if (rule.dataset_id && datasetIds.has(rule.dataset_id)) {
        const ruleName = rule.display_name || "unnamed";
        try {
          const delResp = await fetch(`${apiUrl}/runs/rules/${rule.id}`, {
            method: "DELETE",
            headers: { "x-api-key": apiKey },
          });
          if (delResp.ok) {
            deleted.push(ruleName);
            console.log(`  Deleted evaluator: ${ruleName}`);
          }
        } catch (e) {
          console.log(`  Failed to delete evaluator ${ruleName}: ${e}`);
        }
      }
    }
  } catch (e) {
    console.log(`  Error cleaning up evaluators: ${e}`);
  }

  return deleted;
}

/**
 * Delete all LangSmith resources matching the run_id namespace.
 */
export async function cleanupNamespace(
  args: HandlerArgs
): Promise<{ projects: string[]; evaluators: string[]; datasets: string[] }> {
  const { client, error } = getLangsmithClient();
  if (error || !client) {
    console.log(`Could not cleanup namespace: ${error}`);
    return { projects: [], evaluators: [], datasets: [] };
  }

  const runId = args.run_id;
  if (!runId) {
    return { projects: [], evaluators: [], datasets: [] };
  }

  const deleted: { projects: string[]; evaluators: string[]; datasets: string[] } = {
    projects: [],
    evaluators: [],
    datasets: [],
  };
  const suffix = `-${runId}`;

  // Delete matching projects
  try {
    for await (const project of client.listProjects()) {
      const name = project.name;
      if (name && name.endsWith(suffix)) {
        try {
          await client.deleteProject({ projectName: name });
          deleted.projects.push(name);
          console.log(`  Deleted project: ${name}`);
        } catch (e) {
          console.log(`  Failed to delete project ${name}: ${e}`);
        }
      }
    }
  } catch (e) {
    console.log(`  Error listing projects: ${e}`);
  }

  // Find matching datasets and their IDs (needed for evaluator cleanup)
  const datasetsToDelete: Array<{ name: string; id: string }> = [];
  try {
    for await (const dataset of client.listDatasets()) {
      if (dataset.name.endsWith(suffix)) {
        datasetsToDelete.push({ name: dataset.name, id: dataset.id });
      }
    }
  } catch (e) {
    console.log(`  Error listing datasets: ${e}`);
  }

  // Delete evaluators attached to matching datasets BEFORE deleting datasets
  if (datasetsToDelete.length > 0) {
    const datasetIds = new Set(datasetsToDelete.map((d) => d.id));
    deleted.evaluators = await deleteEvaluatorsForDatasets(datasetIds);
  }

  // Delete matching datasets
  for (const { name } of datasetsToDelete) {
    try {
      await client.deleteDataset({ datasetName: name });
      deleted.datasets.push(name);
      console.log(`  Deleted dataset: ${name}`);
    } catch (e) {
      console.log(`  Failed to delete dataset ${name}: ${e}`);
    }
  }

  return deleted;
}

// =============================================================================
// HANDLER REGISTRY
// =============================================================================

type HandlerFn = (args: HandlerArgs) => Promise<unknown>;

const HANDLERS: Record<string, HandlerFn> = {
  upload_traces: uploadTraces,
  upload_datasets: uploadDatasets,
  cleanup_namespace: cleanupNamespace,
};

/**
 * Run a named handler.
 */
export async function runHandler(handlerName: string, args: HandlerArgs): Promise<unknown> {
  const handler = HANDLERS[handlerName];
  if (!handler) {
    throw new Error(`Unknown handler: ${handlerName}. Available: ${Object.keys(HANDLERS).join(", ")}`);
  }
  return handler(args);
}

/**
 * Run all data handlers for a task.
 */
export async function runTaskHandlers(
  dataHandlers: DataHandler[],
  dataDir: string,
  project: string | null,
  runId: string | null
): Promise<Record<string, string>> {
  let traceIdMap: Record<string, string> = {};

  if (!existsSync(dataDir)) {
    return traceIdMap;
  }

  for (const handler of dataHandlers) {
    const matches = matchFiles(dataDir, handler.pattern);
    if (matches.length > 0) {
      console.log(`\nRunning ${handler.handler}...`);
      const args: HandlerArgs = {
        project: project || undefined,
        data_dir: dataDir,
        run_id: runId || undefined,
        ...(handler.args || {}),
      };
      const result = await runHandler(handler.handler, args);
      if (handler.handler === "upload_traces" && result) {
        traceIdMap = result as Record<string, string>;
      }
    }
  }

  return traceIdMap;
}
