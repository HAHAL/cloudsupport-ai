#!/usr/bin/env bash
set -euo pipefail

HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health}"
MAX_RETRIES="${MAX_RETRIES:-30}"
SLEEP_SECONDS="${SLEEP_SECONDS:-3}"

echo "Checking service health: ${HEALTH_URL}"
for attempt in $(seq 1 "${MAX_RETRIES}"); do
  if curl -fsS "${HEALTH_URL}"; then
    echo "Health check passed."
    exit 0
  fi

  echo "Health check failed, retrying in ${SLEEP_SECONDS} seconds... (${attempt}/${MAX_RETRIES})"
  sleep "${SLEEP_SECONDS}"
done

echo "Health check failed after ${MAX_RETRIES} retries."
exit 1
