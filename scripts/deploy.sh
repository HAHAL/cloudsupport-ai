#!/usr/bin/env bash
set -euo pipefail

echo "Pulling latest code..."
git pull

if [ ! -f .env ]; then
  echo ".env not found, copying from .env.example"
  cp .env.example .env
fi

echo "Building and starting containers..."
docker compose up -d --build

echo "Container status:"
docker compose ps

echo "Running health check..."
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health}" ./scripts/health_check.sh

echo "Deploy completed."
