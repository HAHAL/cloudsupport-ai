#!/usr/bin/env bash
set -euo pipefail

HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health}"

echo "Checking service health: ${HEALTH_URL}"
curl -f "${HEALTH_URL}"
echo "Health check passed."
