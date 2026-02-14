# LangSmith Synergy Test Refactor

## Current State (after this PR)
- `config.py` - shared utilities (skill loading, validators, prompts, CLAUDE.md variants)
- `test_basic.py` - basic treatments with inline section definitions + CLI runner
- `test_advanced.py` - advanced treatments with inline section definitions + CLI runner
- `runner.py` - shared `run_experiment()` function
- Deleted: `conftest.py`, `test_langsmith_synergy.py`, all `skill.py` files

## Future: Shell Script Orchestration

Goal: Language-agnostic test infrastructure so contributors can work in Python or JavaScript.

### Key Insight: Leverage scaffold/ for shared functionality

The `scaffold/` directory already contains substantial shared infrastructure:
- Docker build/run helpers
- Parallel execution (`run_parallel`, `create_work_items`)
- Experiment logging (`ExperimentLogger`)
- Validation framework (`Treatment`, validators)
- Event parsing, output capture, etc.

**Design principle:** Pull as much common functionality into scaffold as possible. Shell scripts should orchestrate, not duplicate logic. Scaffold can have Python-specific and JS-specific components (like loggers) but minimize repeated functionality across tests.

### Proposed Structure
```
tests/langsmith_synergy/
├── run.sh                    # Main entry point (orchestrates)
├── scripts/
│   ├── docker_build.sh       # Wraps scaffold.build_docker_image
│   ├── docker_run.sh         # Wraps scaffold.run_in_docker
│   ├── generate_traces.sh    # Setup LangSmith traces
│   └── cleanup.sh            # Cleanup datasets
├── treatments/
│   ├── basic.json            # Treatment configs (language-agnostic)
│   └── advanced.json
├── validation/
│   ├── run_validators.sh     # Calls language-specific validators
│   ├── validators.py         # Python validators (uses scaffold)
│   └── validators.js         # JS validators
└── python/
    └── conftest.py           # pytest fixtures (if using pytest)

scaffold/
├── __init__.py               # Python exports
├── docker.py                 # Docker helpers (already exists)
├── runner.py                 # run_parallel, create_work_items
├── logger.py                 # ExperimentLogger
├── validators/               # Validator framework
│   ├── base.py               # Shared validator base/interfaces
│   ├── python/               # Python validators
│   │   └── common.py
│   └── js/                   # JS validators
│       └── common.js
└── shell/                    # Shell utilities (new)
    ├── docker.sh             # Reusable docker functions
    ├── parallel.sh           # Parallel execution in shell
    └── logging.sh            # Logging helpers
```

### Benefits
- `./run.sh basic 3` works regardless of language
- Shell scripts thin wrappers around scaffold
- Treatment configs in JSON (language-agnostic)
- Validators can be Python, JS, or both
- Scaffold handles complexity, tests stay simple

### Migration Steps
1. Audit scaffold/ - identify what's already shared vs test-specific
2. Extract more common patterns into scaffold (e.g., ground truth generation)
3. Create shell/ helpers in scaffold for shell script orchestration
4. Convert treatment definitions to JSON
5. Create test-specific run.sh that uses scaffold shell helpers
6. Add JS scaffold components as needed
