#!/usr/bin/env bash
set -u -o pipefail

LOG_DIR=".repair"
LOG_FILE="$LOG_DIR/last_failure.log"
MAX_ATTEMPTS="${MAX_REPAIR_ATTEMPTS:-2}"
REPAIR_COMMAND="${REPAIR_COMMAND:-}"

mkdir -p "$LOG_DIR"

run_checks() {
  bash scripts/verify_all.sh
}

attempt=1
while [[ "$attempt" -le "$MAX_ATTEMPTS" ]]; do
  echo "== verify attempt $attempt/$MAX_ATTEMPTS =="
  if run_checks >"$LOG_FILE" 2>&1; then
    cat "$LOG_FILE"
    echo "All checks passed."
    exit 0
  fi

  echo "Checks failed. Log: $LOG_FILE"
  cat "$LOG_FILE"

  if [[ -z "$REPAIR_COMMAND" ]]; then
    echo "REPAIR_COMMAND is not set. Set it to a local Codex/Claude CLI repair command and rerun."
    echo "Example:"
    echo "  export REPAIR_COMMAND='claude --print < {log}'"
    exit 1
  fi

  if [[ "$REPAIR_COMMAND" == *"{log}"* ]]; then
    command_to_run="${REPAIR_COMMAND//\{log\}/$LOG_FILE}"
  else
    command_to_run="$REPAIR_COMMAND $LOG_FILE"
  fi

  echo "Running repair command: $command_to_run"
  bash -lc "$command_to_run"
  attempt=$((attempt + 1))
done

echo "Repair attempts exhausted."
exit 1
