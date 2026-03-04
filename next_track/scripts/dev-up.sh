#!/usr/bin/env bash
set -euo pipefail

docker compose up -d --build "$@"

# Keep only currently useful image/cache artifacts after rebuild.
docker image prune -f

if docker builder prune --help | grep -q -- "--keep-storage"; then
  docker builder prune -f --keep-storage "${DOCKER_BUILD_CACHE_LIMIT:-4GB}"
else
  docker builder prune -f --filter "until=${DOCKER_BUILD_CACHE_MAX_AGE:-24h}"
fi
