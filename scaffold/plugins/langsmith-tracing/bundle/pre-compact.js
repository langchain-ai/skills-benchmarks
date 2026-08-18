#!/usr/bin/env node

// dist/logger.js
import { appendFileSync, mkdirSync, statSync, renameSync } from "node:fs";
import { dirname } from "node:path";
var MAX_LOG_BYTES = 5 * 1024 * 1024;
var LOG_FILE = process.env.CC_LANGSMITH_LOG_FILE ?? `${process.env.HOME ?? ""}/.claude/state/hook.log`;
var debugEnabled = false;
function initLogger(debug2) {
  debugEnabled = debug2;
  mkdirSync(dirname(LOG_FILE), { recursive: true });
}
function rotateIfNeeded() {
  try {
    if (statSync(LOG_FILE).size >= MAX_LOG_BYTES) {
      renameSync(LOG_FILE, `${LOG_FILE}.1`);
    }
  } catch {
  }
}
function write(level, message) {
  const timestamp = (/* @__PURE__ */ new Date()).toISOString().replace("T", " ").replace("Z", "");
  const line = `${timestamp} [${level}] ${message}
`;
  try {
    rotateIfNeeded();
    appendFileSync(LOG_FILE, line);
  } catch {
  }
}
function error(message) {
  write("ERROR", message);
}
function debug(message) {
  if (debugEnabled) {
    write("DEBUG", message);
  }
}

// dist/state.js
import { readFileSync, writeFileSync, mkdirSync as mkdirSync2, openSync, closeSync, unlinkSync } from "node:fs";
import { dirname as dirname2 } from "node:path";
var LOCK_TIMEOUT_MS = 5e3;
var LOCK_RETRY_MS = 20;
function lockPath(stateFilePath) {
  return `${stateFilePath}.lock`;
}
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
async function acquireLock(stateFilePath) {
  const lock = lockPath(stateFilePath);
  const deadline = Date.now() + LOCK_TIMEOUT_MS;
  mkdirSync2(dirname2(stateFilePath), { recursive: true });
  while (Date.now() < deadline) {
    try {
      const fd = openSync(lock, "wx");
      closeSync(fd);
      return;
    } catch {
      await sleep(LOCK_RETRY_MS);
    }
  }
  try {
    unlinkSync(lock);
  } catch {
  }
}
function releaseLock(stateFilePath) {
  try {
    unlinkSync(lockPath(stateFilePath));
  } catch {
  }
}
async function atomicUpdateState(stateFilePath, fn) {
  await acquireLock(stateFilePath);
  try {
    const state = loadState(stateFilePath);
    writeFileSync(stateFilePath, JSON.stringify(fn(state), null, 2));
  } finally {
    releaseLock(stateFilePath);
  }
}
function loadState(stateFilePath) {
  try {
    const raw = readFileSync(stateFilePath, "utf-8");
    return JSON.parse(raw);
  } catch {
    return {};
  }
}
function getSessionState(state, sessionId) {
  return state[sessionId] ?? {
    last_line: -1,
    turn_count: 0,
    updated: "",
    task_run_map: {}
  };
}
var SESSION_MAX_AGE_MS = 24 * 60 * 60 * 1e3;

// dist/config.js
function loadConfig() {
  const apiKey = process.env.CC_LANGSMITH_API_KEY ?? process.env.LANGSMITH_API_KEY ?? "";
  const project = process.env.CC_LANGSMITH_PROJECT ?? "claude-code";
  const apiBaseUrl = process.env.LANGSMITH_ENDPOINT ?? "https://api.smith.langchain.com";
  const homeDir = process.env.HOME ?? process.env.USERPROFILE ?? "";
  const stateFilePath = process.env.STATE_FILE ?? `${homeDir}/.claude/state/langsmith_state.json`;
  const debug2 = (process.env.CC_LANGSMITH_DEBUG ?? "").toLowerCase() === "true";
  let replicas;
  const providedReplicas = process.env.CC_LANGSMITH_RUNS_ENDPOINTS;
  if (providedReplicas !== void 0) {
    try {
      replicas = JSON.parse(providedReplicas);
    } catch {
      error("Failed to parse provided CC_LANGSMITH_RUNS_ENDPOINTS. Please make sure they are valid JSON.");
    }
  }
  const parentDottedOrder = process.env.CC_LANGSMITH_PARENT_DOTTED_ORDER || void 0;
  let customMetadata;
  const providedMetadata = process.env.CC_LANGSMITH_METADATA;
  if (providedMetadata !== void 0) {
    try {
      const parsed = JSON.parse(providedMetadata);
      if (typeof parsed === "object" && parsed !== null && !Array.isArray(parsed)) {
        customMetadata = parsed;
      } else {
        error("CC_LANGSMITH_METADATA must be a JSON object (not an array or primitive).");
      }
    } catch {
      error("Failed to parse provided CC_LANGSMITH_METADATA. Please make sure it is valid JSON.");
    }
  }
  return {
    apiKey,
    project,
    apiBaseUrl,
    stateFilePath,
    debug: debug2,
    parentDottedOrder,
    replicas,
    customMetadata
  };
}

// dist/utils/hook-init.js
function initHook() {
  const config = loadConfig();
  initLogger(config.debug);
  if (process.env.TRACE_TO_LANGSMITH?.toLowerCase() !== "true") {
    return null;
  }
  if (!config.apiKey && (!config.replicas || config.replicas.length === 0)) {
    error("No API key set (CC_LANGSMITH_API_KEY or LANGSMITH_API_KEY) and no replicas configured");
    return null;
  }
  return config;
}

// dist/utils/stdin.js
function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk) => data += chunk);
    process.stdin.on("end", () => {
      try {
        resolve(JSON.parse(data));
      } catch (err) {
        reject(new Error(`Failed to parse hook input: ${err}`));
      }
    });
    process.stdin.on("error", reject);
  });
}

// dist/hooks/pre-compact.js
async function main() {
  const input = await readStdin();
  const config = initHook();
  if (!config)
    return;
  debug(`PreCompact hook started, session=${input.session_id}, trigger=${input.trigger}`);
  await atomicUpdateState(config.stateFilePath, (state) => {
    const sessionState = getSessionState(state, input.session_id);
    return {
      ...state,
      [input.session_id]: {
        ...sessionState,
        compaction_start_time: Date.now()
      }
    };
  });
  debug(`Recorded compaction start time for session ${input.session_id}`);
}
main().catch((err) => {
  try {
    debug(`PreCompact hook error: ${err}`);
  } catch {
  }
  process.exit(0);
});
