# LangSmith Sandbox Migration Plan

## What This Is

Harbor supports `--env langsmith` as a compute environment. Instead of running
the agent and verifier in local Docker containers, Harbor provisions a
**LangSmith Sandbox** (a remote VM) and runs everything there.

This is **not** a tracing integration — Claude Code traces do not automatically
appear in LangSmith. It only changes *where* the containers execute.

## Current State

- All 20 tasks converted to Harbor format in `harbor_tasks/`
- `scripts/sweep.py` orchestrates runs via `scripts/harbor_run.sh`
- `harbor_run.sh` calls `harbor run --env-file .env ... "$@"` — passes remaining
  args through, currently defaults to local Docker
- `.env` has `LANGSMITH_API_KEY`, which is all the sandbox needs for auth

## Key Fact: No Network Config Needed

Harbor's `network_mode` **defaults to `public`** (`harbor/models/task/config.py:31,146-148`).
The LangSmith env is internet-on by default (`environments/langsmith.py:1068-1072`).
The LangSmith sandbox itself allows HTTP/HTTPS to any host by default — only raw
TCP is blocked. Both `api.anthropic.com` and `api.smith.langchain.com` are HTTPS.

**So both agent and verifier already have outbound HTTPS with zero network
config.** No `network_mode` backfill and no `convert_task.py` change is required.
(`allow_internet` is the deprecated field; `network_mode` is current — but the
default already covers us.)

## Setup (required for `--env langsmith`)

Harbor is **pinned to 0.18.0** (Python 3.13). Two LangSmith-sandbox fixes are not
yet in a Harbor release, so we patch the installed package after install:

```bash
uv tool install 'harbor[langsmith]==0.18.0' --python 3.13
uv run python scripts/patch_harbor.py    # idempotent; re-run after any reinstall
```

- The `[langsmith]` extra is NOT in the base install; without it you get
  `MissingExtraError: pip install 'harbor[langsmith]'`.
- `scripts/patch_harbor.py` verifies the version is 0.18.0, then applies fix #1 and
  fix #3 (below) idempotently, erroring clearly if the code has changed.

## Changes Made

### `scripts/sweep.py` — `--env` flag (commit d123a0b)

Added `-e/--env` (default `docker`), threaded through `run_cell()` into the harbor
argv as `--env <env>`. `harbor_run.sh` forwards `"$@"`, so it flows through.

### `scripts/harbor_run.sh` — build-timeout bump (commit d123a0b)

Added `--environment-build-timeout-multiplier 5`. First-run remote snapshot builds
exceed the default 600s ceiling. Harmless for docker (local builds are fast).

### `harbor_tasks/ls-multiskill-basic/task.toml` — builder sizing

`[environment]` now sets `cpus = 4`, `memory_mb = 8192`, `storage_mb = 65536`,
`build_timeout_sec = 1800`. These feed the snapshot builder (via fix #1).

### `scripts/patch_harbor.py` — the two Harbor patches

Fix #1 and fix #3 applied to the installed Harbor package (see below).

## Root Cause (fully diagnosed) — three infra issues, none in our code

Confirmed end-to-end by building the real task image directly via the LangSmith
SDK. Workspace, permissions, egress, and our task image are all fine.

1. **Builder underpowered** (Harbor gap) — `_create_dockerfile_snapshot` never
   passed `vcpus`/`mem_bytes`, so the snapshot builder OOM'd/stalled on the full
   langchain stack. With 4 vCPU / 8 GiB, pip dropped ~290s → 33s and the build
   succeeded. **Fix #1** forwards the task's cpu/memory to the builder (still
   broken on upstream main → PR candidate).
2. **Snapshot builder disk too small** — default 32 GiB. Raised via task.toml
   `storage_mb = 65536`.
3. **Untagged-snapshot lookup** (SDK/Harbor gap) — dockerfile-built snapshots are
   stored untagged, but `create_sandbox` resolves a bare name to `<name>:latest`
   → 404. **Fix #3** boots by snapshot **id** instead. Already fixed on upstream
   main; our patch backports it to the 0.18.0 release.

With all three applied, `ls-multiskill-basic --env langsmith` runs end-to-end:
build → snapshot → run sandbox → agent → verifier → cleanup, producing real
verifier results (CONTROL: reward 0.0, expected for the no-skills baseline).

## Next Steps

- **Open a Harbor PR** for **fix #1** (builder cpu/memory sizing) against `main` —
  it is the only fix still missing upstream. Fix #3 is already on main.
- **Drop the local patch** once a Harbor release ships fix #1; then bump the pin
  and delete `scripts/patch_harbor.py`.
- **Egress is NOT a blocker** — `network_mode` defaults to public; no task.toml
  network changes needed.

## Caveats

- **Cost**: each run provisions a paid remote VM. Factor into run budgets.
- **First-run latency**: first run per task builds a remote snapshot (slow);
  later runs reuse the cached snapshot (keyed by Dockerfile hash + env).
- **Not Claude Code tracing**: the agent runs remotely, but its tool calls/
  messages do not appear as LangSmith traces (separate stop-hook, out of scope).
