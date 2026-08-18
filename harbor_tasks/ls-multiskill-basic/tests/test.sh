#!/usr/bin/env bash
# Run the ported validation checks and translate the result into a Harbor reward.
set -uo pipefail

export BENCH_TEST_CONTEXT="/tests/_test_context.json"
export BENCH_TEST_RESULTS="/logs/verifier/_test_results.json"
mkdir -p /logs/verifier

cd "/workspace" || exit 1
export PYTHONPATH="/tests:${PYTHONPATH:-}"

# Inject RUN_ID into test context so validators can scope LangSmith queries.
if [ -n "${RUN_ID:-}" ]; then
  python3 -c "
import json, sys
path = '/tests/_test_context.json'
with open(path) as f:
    ctx = json.load(f)
ctx['run_id'] = sys.argv[1]
with open(path, 'w') as f:
    json.dump(ctx, f, indent=2)
" "$RUN_ID"
fi

status=0
python /tests/test_dataset.py
status=$((status | $?))

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
