/**
 * Output parsing, event extraction, and experiment logging.
 */

import { existsSync, mkdirSync, writeFileSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
export const PROJECT_ROOT = resolve(__dirname, "..", "..");
export const LOGS_DIR = join(PROJECT_ROOT, "logs");

// eslint-disable-next-line no-control-regex
const ANSI_ESCAPE = /\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])/g;
const NPM_NOISE = [/^npm warn exec.*$/gm, /^npm notice.*$/gm];

export function stripAnsi(text: string): string {
  return text.replace(ANSI_ESCAPE, "");
}

export function stripNpmNoise(text: string): string {
  let result = text;
  for (const pattern of NPM_NOISE) result = result.replace(pattern, "");
  return result.replace(/\n{3,}/g, "\n\n").trim();
}

export function cleanOutput(text: string): string {
  return stripNpmNoise(stripAnsi(text));
}

// =============================================================================
// OUTPUT PARSING
// =============================================================================

export interface ParsedOutput {
  messages: Record<string, unknown>[];
}

/** Parse stream-json output into structured data. */
export function parseOutput(stdout: string): ParsedOutput {
  if (!stdout) return { messages: [] };
  const messages: Record<string, unknown>[] = [];
  for (const line of stdout.trim().split("\n")) {
    try { messages.push(JSON.parse(line)); } catch { /* skip non-JSON */ }
  }
  return { messages };
}

// =============================================================================
// EVENT EXTRACTION
// =============================================================================

export interface ToolCall {
  tool: string;
  input: Record<string, unknown>;
  output?: string;
}

export interface Events {
  tool_calls: ToolCall[];
  files_read: string[];
  files_created: string[];
  files_modified: string[];
  commands_run: string[];
  skills_invoked: string[];
  duration_seconds: number | null;
  num_turns: number | null;
}

/**
 * Extract events (tool calls, files, etc.) from parsed output.
 */
export function extractEvents(parsed: ParsedOutput): Events {
  const events: Events = {
    tool_calls: [],
    files_read: [],
    files_created: [],
    files_modified: [],
    commands_run: [],
    skills_invoked: [],
    duration_seconds: null,
    num_turns: null,
  };

  // Map tool_use_id -> index in tool_calls list for matching outputs
  const toolIdToIndex: Record<string, number> = {};

  for (const msg of parsed.messages) {
    if (msg.type === "result") {
      const durationMs = msg.duration_ms as number | undefined;
      events.duration_seconds = durationMs ? durationMs / 1000 : null;
      events.num_turns = (msg.num_turns as number) ?? null;
    }

    if (msg.type === "assistant") {
      const message = msg.message as Record<string, unknown> | undefined;
      const content = (message?.content as unknown[]) || [];

      for (const item of content) {
        const itemObj = item as Record<string, unknown>;
        if (itemObj.type === "tool_use") {
          const tool = (itemObj.name as string) || "";
          const inp = (itemObj.input as Record<string, unknown>) || {};
          const toolId = itemObj.id as string | undefined;

          const toolCall: ToolCall = { tool, input: inp };
          if (toolId) {
            toolIdToIndex[toolId] = events.tool_calls.length;
          }
          events.tool_calls.push(toolCall);

          const path = (inp.file_path as string) || "";
          if (tool === "Read" && path) {
            events.files_read.push(path);
          } else if (tool === "Write" && path) {
            events.files_created.push(path);
          } else if (tool === "Edit" && path) {
            events.files_modified.push(path);
          } else if (tool === "Bash" && inp.command) {
            events.commands_run.push(inp.command as string);
          } else if (tool === "Skill" && inp.skill) {
            events.skills_invoked.push(inp.skill as string);
          }
        }
      }
    }

    // Capture tool results and match to their tool_use calls
    if (msg.type === "user") {
      const message = msg.message as Record<string, unknown> | undefined;
      const content = (message?.content as unknown[]) || [];

      for (const item of content) {
        const itemObj = item as Record<string, unknown>;
        if (itemObj.type === "tool_result") {
          const toolUseId = itemObj.tool_use_id as string | undefined;
          if (toolUseId && toolUseId in toolIdToIndex) {
            const idx = toolIdToIndex[toolUseId];
            let outputContent = itemObj.content;

            if (Array.isArray(outputContent)) {
              outputContent = outputContent
                .map((c) => {
                  if (typeof c === "object" && c !== null && "text" in c) {
                    return (c as Record<string, unknown>).text;
                  }
                  return String(c);
                })
                .join(" ");
            }

            events.tool_calls[idx].output = String(outputContent);
          }
        }
      }
    }
  }

  return events;
}

// =============================================================================
// TREATMENT RESULT
// =============================================================================

export interface EventsSummary {
  duration_seconds?: number | null;
  num_turns?: number | null;
  tool_calls?: number;
  files_created?: string[];
  skills_invoked?: string[];
}

export interface TreatmentResult {
  name: string;
  passed: boolean;
  checks_passed: string[];
  checks_failed: string[];
  events_summary: EventsSummary;
  run_id: string;
}

export function createTreatmentResult(
  name: string,
  checksPassed: string[],
  checksFailed: string[],
  events: Events,
  runId = ""
): TreatmentResult {
  return {
    name,
    passed: checksFailed.length === 0,
    checks_passed: checksPassed,
    checks_failed: checksFailed,
    events_summary: {
      duration_seconds: events.duration_seconds,
      num_turns: events.num_turns,
      tool_calls: events.tool_calls.length,
    },
    run_id: runId,
  };
}

export function hasCheck(result: TreatmentResult, pattern: string): boolean {
  return result.checks_passed.some((c) => c.includes(pattern));
}

export function hasFailedCheck(result: TreatmentResult, pattern: string): boolean {
  return result.checks_failed.some((c) => c.includes(pattern));
}

// =============================================================================
// REPORT COLUMNS
// =============================================================================

export interface ReportColumn {
  name: string;
  description?: string;
  extract: (result: TreatmentResult) => string;
  aggregate?: (runs: TreatmentResult[]) => string;
}

export function boolColumn(name: string, pattern: string, description?: string): ReportColumn {
  return {
    name,
    description: description || `Checks if any passed check contains: \`${pattern}\``,
    extract: (r) => hasCheck(r, pattern) ? "Yes" : "No",
    aggregate: (runs) => `${runs.filter((r) => hasCheck(r, pattern)).length}/${runs.length}`,
  };
}

export function qualityColumn(name = "Quality"): ReportColumn {
  return {
    name,
    description: "Checks for [GOOD] or [LOW] quality rating from LLM evaluation",
    extract: (r) => {
      for (const c of r.checks_passed) {
        if (c.includes("[GOOD]")) return "Good";
        if (c.includes("[LOW]")) return "Low";
      }
      return "N/A";
    },
    aggregate: (runs) => `${runs.filter((r) => r.checks_passed.some((c) => c.includes("[GOOD]"))).length}/${runs.length}`,
  };
}

function formatChecks(r: TreatmentResult): string {
  const passed = r.checks_passed.length;
  const total = passed + r.checks_failed.length;
  const pct = total > 0 ? (passed / total) * 100 : 0;
  return `${passed}/${total} (${pct.toFixed(0)}%)`;
}

function aggregateChecks(runs: TreatmentResult[]): string {
  const totalPassed = runs.reduce((sum, r) => sum + r.checks_passed.length, 0);
  const totalChecks = runs.reduce(
    (sum, r) => sum + r.checks_passed.length + r.checks_failed.length,
    0
  );
  const pct = totalChecks > 0 ? (totalPassed / totalChecks) * 100 : 0;
  return `${totalPassed}/${totalChecks} (${pct.toFixed(0)}%)`;
}

function avg(values: (number | null | undefined)[], format: (n: number) => string): string {
  const filtered = values.filter((v): v is number => v != null);
  if (filtered.length === 0) return "N/A";
  return format(filtered.reduce((a, b) => a + b, 0) / filtered.length);
}

/**
 * Standard columns: Checks, Turns, Duration, Tools.
 */
export function defaultColumns(): ReportColumn[] {
  return [
    {
      name: "Checks",
      extract: formatChecks,
      aggregate: aggregateChecks,
    },
    {
      name: "Turns",
      extract: (r) => (r.events_summary.num_turns?.toString() ?? "N/A"),
      aggregate: (runs) =>
        avg(
          runs.map((r) => r.events_summary.num_turns),
          (n) => n.toFixed(0)
        ),
    },
    {
      name: "Duration",
      extract: (r) =>
        r.events_summary.duration_seconds != null
          ? `${r.events_summary.duration_seconds.toFixed(0)}s`
          : "N/A",
      aggregate: (runs) =>
        avg(
          runs.map((r) => r.events_summary.duration_seconds),
          (n) => `${n.toFixed(0)}s`
        ),
    },
    {
      name: "Tools",
      extract: (r) => r.events_summary.tool_calls?.toString() ?? "N/A",
      aggregate: (runs) =>
        avg(
          runs.map((r) => r.events_summary.tool_calls),
          (n) => n.toFixed(0)
        ),
    },
  ];
}

// =============================================================================
// EXPERIMENT LOGGER
// =============================================================================

export class ExperimentLogger {
  experimentId: string;
  name: string;
  timestamp: string;
  baseDir: string;
  eventsDir: string;
  reportsDir: string;
  rawDir: string;
  columns: ReportColumn[];
  results: Record<string, TreatmentResult[]>;
  metadata: {
    experiment_id: string;
    started_at: string;
    treatments: string[];
    completed_at?: string;
    total_runs?: number;
    total_passed?: number;
  };

  constructor(options: {
    experimentName?: string;
    columns?: ReportColumn[];
    experimentId?: string;
  } = {}) {
    const { experimentName, columns = [], experimentId } = options;

    if (experimentId) {
      // Join existing experiment
      this.experimentId = experimentId;
      this.name = experimentId.includes("_")
        ? experimentId.split("_").slice(0, -2).join("_")
        : experimentId;
      this.timestamp = experimentId.includes("_")
        ? experimentId.split("_").slice(-1)[0]
        : "";
    } else {
      // Create new experiment
      this.timestamp = new Date().toISOString().replace(/[-:]/g, "").slice(0, 15).replace("T", "_");
      this.name = experimentName || `experiment_${this.timestamp}`;
      this.experimentId = `${this.name}_${this.timestamp}`;
    }

    this.baseDir = join(LOGS_DIR, "experiments", this.experimentId);
    this.eventsDir = join(this.baseDir, "events");
    this.reportsDir = join(this.baseDir, "reports");
    this.rawDir = join(this.baseDir, "raw");

    // Create directories
    for (const dir of [this.eventsDir, this.reportsDir, this.rawDir]) {
      mkdirSync(dir, { recursive: true });
    }

    this.columns = columns;
    this.results = {};
    this.metadata = {
      experiment_id: this.experimentId,
      started_at: new Date().toISOString(),
      treatments: [],
    };
  }

  addResult(treatmentName: string, result: TreatmentResult): void {
    if (!(treatmentName in this.results)) {
      this.results[treatmentName] = [];
      this.metadata.treatments.push(treatmentName);
    }
    this.results[treatmentName].push(result);
  }

  private getAllColumns(): ReportColumn[] {
    const defaults = defaultColumns();
    const passCol = defaults[0];
    const metricCols = defaults.slice(1);
    return [passCol, ...this.columns, ...metricCols];
  }

  generateSummary(): string {
    const lines: string[] = [];
    lines.push("# Experiment Results Summary\n");
    lines.push(`**Experiment ID:** \`${this.experimentId}\`\n`);
    lines.push(`**Started:** ${this.metadata.started_at}\n`);
    lines.push(`**Completed:** ${new Date().toISOString()}\n`);
    lines.push("");

    const columns = this.getAllColumns();
    const hasReps = Object.values(this.results).some((runs) => runs.length > 1);

    // Column definitions section
    const customCols = this.columns.filter((c) => c.description);
    if (customCols.length > 0) {
      lines.push("## Column Definitions\n");
      for (const col of customCols) {
        lines.push(`- **${col.name}**: ${col.description}`);
      }
      lines.push("");
    }

    const colNames = ["Treatment", ...columns.map((c) => c.name)];
    const header = "| " + colNames.join(" | ") + " |";
    const separator = "|" + colNames.map((n) => "-".repeat(n.length + 2)).join("|") + "|";

    lines.push(hasReps ? "## Results (with Repetitions)\n" : "## Results\n");
    lines.push(header);
    lines.push(separator);

    for (const [name, runs] of Object.entries(this.results)) {
      const values = columns.map((c) =>
        hasReps && c.aggregate ? c.aggregate(runs) : c.extract(runs[0])
      );
      lines.push(`| ${name} | ${values.join(" | ")} |`);
    }

    lines.push("");

    const totalRuns = Object.values(this.results).reduce((sum, runs) => sum + runs.length, 0);
    const totalChecksPassed = Object.values(this.results).reduce(
      (sum, runs) => sum + runs.reduce((s, r) => s + r.checks_passed.length, 0),
      0
    );
    const totalChecks = Object.values(this.results).reduce(
      (sum, runs) =>
        sum + runs.reduce((s, r) => s + r.checks_passed.length + r.checks_failed.length, 0),
      0
    );
    const checkPct = totalChecks > 0 ? (totalChecksPassed / totalChecks) * 100 : 0;

    lines.push("## Summary\n");
    lines.push(`- **Total Runs:** ${totalRuns}`);
    lines.push(`- **Checks Passed:** ${totalChecksPassed}/${totalChecks} (${checkPct.toFixed(1)}%)`);
    lines.push("");

    // Detailed per-treatment breakdown
    lines.push("## Treatment Details\n");
    for (const [name, runs] of Object.entries(this.results)) {
      const treatmentPassed = runs.reduce((sum, r) => sum + r.checks_passed.length, 0);
      const treatmentTotal = runs.reduce(
        (sum, r) => sum + r.checks_passed.length + r.checks_failed.length,
        0
      );
      const treatmentPct = treatmentTotal > 0 ? (treatmentPassed / treatmentTotal) * 100 : 0;
      lines.push(
        `### ${name} (${treatmentPassed}/${treatmentTotal} checks, ${treatmentPct.toFixed(0)}%)\n`
      );

      for (let i = 0; i < runs.length; i++) {
        const r = runs[i];
        const runLabel = hasReps ? `Run ${i + 1}` : "Result";
        const runPassed = r.checks_passed.length;
        const runTotal = runPassed + r.checks_failed.length;
        const runPct = runTotal > 0 ? (runPassed / runTotal) * 100 : 0;
        const runIdStr = r.run_id ? ` (run_id: ${r.run_id})` : "";
        lines.push(`**${runLabel}:** ${runPassed}/${runTotal} checks (${runPct.toFixed(0)}%)${runIdStr}`);

        // Show metrics
        const metrics: string[] = [];
        if (r.events_summary.num_turns != null) {
          metrics.push(`Turns: ${r.events_summary.num_turns}`);
        }
        if (r.events_summary.duration_seconds != null) {
          metrics.push(`Duration: ${r.events_summary.duration_seconds.toFixed(0)}s`);
        }
        if (r.events_summary.tool_calls != null) {
          metrics.push(`Tool calls: ${r.events_summary.tool_calls}`);
        }
        if (metrics.length > 0) {
          lines.push(`- Metrics: ${metrics.join(", ")}`);
        }

        // Show all passed checks
        if (r.checks_passed.length > 0) {
          lines.push(`- Passed checks (${r.checks_passed.length}):`);
          for (const check of r.checks_passed) {
            lines.push(`  - ${check}`);
          }
        }

        // Show all failed checks
        if (r.checks_failed.length > 0) {
          lines.push(`- Failed checks (${r.checks_failed.length}):`);
          for (const check of r.checks_failed) {
            lines.push(`  - ${check}`);
          }
        }

        lines.push("");
      }
    }

    return lines.join("\n");
  }

  finalize(): string {
    const summary = this.generateSummary();
    const summaryPath = join(this.baseDir, "summary.md");
    writeFileSync(summaryPath, summary);

    this.metadata.completed_at = new Date().toISOString();
    this.metadata.total_runs = Object.values(this.results).reduce(
      (sum, runs) => sum + runs.length,
      0
    );
    this.metadata.total_passed = Object.values(this.results).reduce(
      (sum, runs) => sum + runs.filter((r) => r.passed).length,
      0
    );

    const metadataPath = join(this.baseDir, "metadata.json");
    writeFileSync(metadataPath, JSON.stringify(this.metadata, null, 2));

    console.log(`\nExperiment results saved to: ${this.baseDir}`);
    console.log(`Summary: ${summaryPath}`);

    return summaryPath;
  }
}

// =============================================================================
// PARALLEL SAVE HELPERS
// =============================================================================

export function saveEvents(baseDir: string, treatmentName: string, rep: number, events: Events): string {
  const dir = join(baseDir, "events");
  mkdirSync(dir, { recursive: true });
  const path = join(dir, `${treatmentName.toLowerCase()}_rep${rep}.json`);
  writeFileSync(path, JSON.stringify(events, null, 2));
  return path;
}

export function saveRaw(baseDir: string, treatmentName: string, rep: number, stdout: string, stderr?: string): void {
  const dir = join(baseDir, "raw");
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, `${treatmentName.toLowerCase()}_rep${rep}_stdout.json`), stdout);
  if (stderr) writeFileSync(join(dir, `${treatmentName.toLowerCase()}_rep${rep}_stderr.txt`), stderr);
}

export function saveReport(baseDir: string, treatmentName: string, rep: number, report: Record<string, unknown>): string {
  const dir = join(baseDir, "reports");
  mkdirSync(dir, { recursive: true });
  const path = join(dir, `${treatmentName.toLowerCase()}_rep${rep}_report.json`);
  writeFileSync(path, JSON.stringify(report, null, 2));
  return path;
}

export function loadResultsFromReports(reportsDir: string): TreatmentResult[] {
  if (!existsSync(reportsDir)) return [];
  const results: TreatmentResult[] = [];

  for (const file of readdirSync(reportsDir).filter((f) => f.endsWith(".json")).sort()) {
    try {
      const report = JSON.parse(readFileSync(join(reportsDir, file), "utf8")) as Record<string, unknown>;
      results.push({
        name: (report.name as string) || "unknown",
        passed: (report.passed as boolean) ?? false,
        checks_passed: (report.checks_passed as string[]) || [],
        checks_failed: (report.checks_failed as string[]) || [],
        events_summary: (report.events_summary as EventsSummary) || {},
        run_id: (report.run_id as string) || "",
      });
    } catch { /* skip invalid */ }
  }
  return results;
}
