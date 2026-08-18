#!/usr/bin/env bash
# Run the ported validation checks and translate the result into a Harbor reward.
set -uo pipefail

export BENCH_TEST_CONTEXT="/tests/_test_context.json"
export BENCH_TEST_RESULTS="/logs/verifier/_test_results.json"
mkdir -p /logs/verifier

cd "/workspace" || exit 1
export PYTHONPATH="/tests:${PYTHONPATH:-}"

status=0
python /tests/test_streaming.py
status=$((status | $?))

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
