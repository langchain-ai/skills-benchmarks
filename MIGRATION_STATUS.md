# Skills-Benchmarks → Harbor Migration — Status

_Last updated: 2026-07-17_

Single source of truth for the migration from the bespoke pytest + `docker.sh`
harness to the **Harbor** agent-eval framework, including the LangSmith Sandbox
compute backend. Consolidates the prior scattered plan/handoff/notes docs.

---

## TL;DR

- **Harness:** migrated to Harbor. Treatments are lists of skill refs; Harbor
  injects them natively via `--skills <dir>`. No custom agent, no CLAUDE.md
  injection, no XML parsing. Driven by `scripts/sweep.py`.
- **Tasks:** all 20 tasks converted to Harbor format under `harbor_tasks/`.
- **LangSmith sandbox (`--env langsmith`): working.** Runs end-to-end on a remote
  LangSmith VM. Requires pinned+patched Harbor (below). Validated end-to-end on
  `ls-multiskill-basic` and `lc-basic`; the other 18 are configured identically
  but not each individually smoke-tested.
- **Upstream PR** for the one still-missing Harbor fix is **approved, not yet merged**
  (harbor-framework/harbor#2356).

---

## Architecture

### Skills — two bring-in modes (auto-detected per ref)
1. **Whole-file:** a dir containing `SKILL.md` (bundled files like `references/`
   copied along), or a single loose `.md`. This is `skills/main/*`, `skills/noise/*`.
2. **Decomposed:** a dir with `skill.yaml` + `sections/`, rendered on demand by
   `skillbench_harbor/skill_render.py`. `sections/<id>.md` is shared prose;
   `<id>.py.md` / `<id>.ts.md` are per-section language variants (single-sources
   shared prose so py/ts can't drift). Output is clean markdown, no XML.
   Legacy `skill_all.md`/`skill_py.md`/`skill_ts.md` remain as sources but are
   ignored at render.

### Treatments
- A treatment = `{description, skills: [refs]}`. `CONTROL` = `[]`.
- A **skill ref is a path relative to `skills/`** (e.g. `main/langchain-fundamentals`,
  `benchmarks/oss_merged/da_core`, `noise/api_docs`).
- Treatment YAMLs live under `treatments/<category>/*.yaml`; the loader scans
  recursively and **skips any dir starting with `_`** (so `treatments/_archive/`
  is parked). ~23 active treatments: `CONTROL`, `ALL_MAIN_SKILLS`, `MAIN_*`,
  `LS_*`, `LCC_*`, `OSSM_BASE`, `OSSS_*`.

### Running it
```bash
# CONTROL vs ALL_MAIN_SKILLS on one task, sonnet, n=1
uv run python scripts/sweep.py --task harbor_tasks/oss-fix-lc-streaming \
  --treatment CONTROL,ALL_MAIN_SKILLS -m anthropic/claude-sonnet-4-6

# other agent + TS variants + globbed treatments + reps
uv run python scripts/sweep.py --task <t> --treatment 'OSSS_*' \
  --agent codex --language ts --count 3

# run on the LangSmith sandbox instead of local Docker
uv run python scripts/sweep.py --task <t> --treatment CONTROL --env langsmith
```
`sweep.py` stages each treatment into `.sweep/skills/<treatment>[-lang]/` (gitignored),
then runs `scripts/harbor_run.sh --path <task> --agent <name> -m <model> --skills <dir>`
(omits `--skills` for CONTROL), and parses each job's `verifier/{reward.txt,_test_results.json}`
into a table + `sweep-summary.json`.

**Gotcha:** the eval agent's LLM calls route through the **LangSmith LLM Gateway**,
not direct Anthropic. `.env` sets `ANTHROPIC_BASE_URL=https://gateway.smith.langchain.com/anthropic`
and `ANTHROPIC_API_KEY=${LANGSMITH_API_KEY}`; `harbor_run.sh` no longer unsets the
base URL. Pass a **bare** model id (`claude-sonnet-4-6`, no `anthropic/` prefix) —
under a custom base URL the claude-code adapter forwards the model string verbatim
(`claude_code.py:1381-1386`).

---

## LangSmith Sandbox (`--env langsmith`) — DONE

Runs the agent + verifier on a remote LangSmith VM instead of local Docker. This
is **not** a Claude Code tracing integration — it only changes where containers run.

### Required setup
```bash
uv tool install 'harbor[langsmith]==0.18.0' --python 3.13
uv run python scripts/patch_harbor.py    # idempotent; re-run after any reinstall
```
- The `[langsmith]` extra is NOT in the base install (else `MissingExtraError`).
- **LLM auth = LangSmith LLM Gateway.** `.env` sets `ANTHROPIC_BASE_URL` (the
  gateway) + `ANTHROPIC_API_KEY=${LANGSMITH_API_KEY}`; the gateway resolves the
  real Anthropic key from the workspace's **gateway provider secrets**. So the
  gateway beta must be enabled on the active workspace (`chat-lc-lite` / Demo
  Workspace) with a **valid Anthropic provider secret** registered (a dead
  provider secret surfaces as Anthropic's `401 "API key is invalid"`). Verify
  with the curl probe before a run. `LANGSMITH_API_KEY` also authenticates
  sandbox provisioning.
- Harbor is **pinned to 0.18.0** deliberately (see patches below).

### Root cause of the three issues (all infra, none in repo code)
1. **Builder underpowered** — `_create_dockerfile_snapshot` never passed
   `vcpus`/`mem_bytes`, so the snapshot builder OOM'd/stalled on the full
   LangChain stack (pip ~290s → 33s once sized). **Fix #1**: forward task
   cpu/memory. *Still missing upstream → the open PR.*
2. **Builder disk too small** (default 32 GiB). Raised via task.toml `storage_mb`.
3. **Untagged-snapshot 404** — `create_sandbox` resolves a bare name to
   `<name>:latest`; dockerfile-built snapshots are untagged. **Fix #3**: boot by
   snapshot id. *Already on upstream `main`; our patch backports it to 0.18.0.*

### What makes it work (all committed / in place)
- `scripts/sweep.py`: `-e/--env` flag (default `docker`) — commit d123a0b.
- `scripts/harbor_run.sh`: `--environment-build-timeout-multiplier 5` — commit d123a0b.
- **All 20 tasks** `[environment]`: `cpus=4, memory_mb=8192, storage_mb=65536,
  build_timeout_sec=1800`; `convert_task.py` emits the same for future tasks —
  commit b6a6900.
- `scripts/patch_harbor.py`: applies fix #1 + fix #3 to the installed 0.18.0
  package (idempotent, version-checked).

### Key facts
- **Egress is NOT a blocker.** `network_mode` defaults to `public`; the sandbox
  allows outbound HTTP/HTTPS to any host (only raw TCP blocked). `api.anthropic.com`,
  `api.smith.langchain.com`, and `gateway.smith.langchain.com` are all HTTPS.
  (`allow_internet` is the deprecated field; `network_mode` is current.) A task
  set to `no-network` would block the gateway and cannot be per-host allowlisted
  on LangSmith — keep tasks on the default `public`.
- Faithful to Docker: identical task+treatment gives identical results on
  `--env langsmith` and `--env docker`.
- Each run provisions a **paid** VM. First run per task builds a slow remote
  snapshot; later runs reuse the cache (keyed by Dockerfile hash + env).
- **Run long sweeps under `caffeinate -s`** — if the host sleeps mid-run, host-side
  LangSmith calls fail with DNS `NameResolutionError` and the run is wrecked.

### Upstream PR
- harbor-framework/harbor#2356 — fix #1 (builder cpu/memory). **Approved**
  (by `alexgshaw`), not yet merged. Once a release ships it, bump the pin and
  delete `scripts/patch_harbor.py` (fix #3 is already on main).

---

## Harbor task/schema facts
- `task.toml` `schema_version = "1.3"`. Sections: `[task]` (`name` = `org/name`),
  `[metadata]`, `[agent].timeout_sec`, `[verifier].timeout_sec`, `[environment]`
  (`docker_image` or `environment/Dockerfile`, `workdir`, resources, optional
  `[environment.env]`).
- Verifier runs `tests/test.sh` from workdir; `tests/` mounts at `/tests`; reward →
  `/logs/verifier/reward.txt` (`reward.json` preferred if present).
- LangSmith sandboxes run commands from `/`, not the image WORKDIR — Harbor probes
  `readlink /proc/1/cwd` to detect it.
- Reference implementation to mirror for reporting: `langchain-ai/deepagents` →
  `libs/evals/deepagents_harbor/`.

---

## Last known benchmark signal (pre-Harbor harness — rerun on Harbor still pending)
From `experiment_20260518_212749`, 11 `lc-*` tasks × 3 reps:
- CONTROL **12%** (4/33), MAIN_FRAMEWORK_SELECTION **73%** (24/33),
  MAIN_ECOSYSTEM_PRIMER **79%** (26/33). Both primers ~6× CONTROL.
- `lc-ecosystem-env-setup` is a **discoverability (trigger) problem, not content** —
  primers score 0/3 despite ~82% check pass-rate because the frontmatter
  `description:` doesn't match a "give me an env file" prompt. Fix = widen the
  frontmatter on `ecosystem-primer/SKILL.md` + `framework-selection/SKILL.md`.
- `lc-framework-hybrid-pipeline` is the hardest task (no treatment hits 3/3).

---

## Skill-authoring learnings (carried from jacob-notes)
- **Separate the failure modes:** trigger (did the skill fire?) vs chaining (did it
  pull in the right follow-on skills?) vs content (was the guidance correct?). The
  skill **`description:` controls triggering** — fix it for trigger problems; edit
  the body for chaining/content. A skill can have great content and still score 0
  if it never triggers.
- **Validators statically grep source** → watch for false positives (e.g. Claude
  commenting out a call but leaving the import passes a naive regex). Per repo
  CLAUDE.md: always verify validators manually — inspect the transcript + modified
  files even on PASS.
- The `lc-framework-*` validators assert canonical current APIs (LangChain
  `create_agent`, LangGraph `StateGraph`, Deep Agents `create_deep_agent`); keep
  these in sync as those libraries evolve.

---

## Known loose ends / next steps
1. **Adapt validators to ref-based treatments.** Per-task validators and
   `tests/conftest.py` event-extraction (`skills_invoked`) were written against the
   old skill/treatment layout. **Do not delete these — they are the kept contract**
   (`scaffold/python/validation/*` = `TestRunner`/`_test_results`).
2. **Legacy orchestrators** `tests/tasks/test_tasks.py` + `.test.ts` import the
   removed `build_treatment_skills` and fail to collect — decide delete vs rewrite.
   They don't affect `sweep.py`/Harbor.
3. **Run a real benchmark at `--count 3+`** — n=1 is noisy (CONTROL seen at 2/5 and
   3/5). Confirm `ALL_MAIN_SKILLS ≥ CONTROL` at n≥3.
4. **Task-signal issue:** `ALL_MAIN_SKILLS == CONTROL` on `ls-multiskill-basic`
   (both docker and langsmith) — that task's validator isn't discriminating skills.
5. **Validate multi-agent for real** — only `claude-code` has been run; smoke-test
   `--agent codex` and `--agent langgraph` (deepagents).
6. **Validate the 4 `ls-trace-*` tasks** (crewai, openai-agents, pydantic-ai,
   google-adk) under the Harbor pipeline (`GOOGLE_API_KEY` needed for google-adk).
7. **Smoke-test the remaining 18 tasks on `--env langsmith`** (configured, not yet
   individually run).
8. `npm run typecheck` after trimming `scaffold/typescript/index.ts`.

### macOS local-Docker gotchas (still valid for `--env docker`)
- `gtimeout` required (`brew install coreutils`) — without it `docker.sh` runs with
  no timeout → hung containers burn API spend.
- `Docker.raw` grows unboundedly; reclaim by deleting it with Docker quit.
