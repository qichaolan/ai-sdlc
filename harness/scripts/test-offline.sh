#!/usr/bin/env bash
# Run the tests in a disposable container with no network.
#
# Step 1 installs locked dependencies with network access into
# .sandbox/venv. Step 2 runs the command with --network=none, resource
# limits, no Linux capabilities, and a timeout. The host's .venv and
# credentials are never mounted.
#
# Usage: scripts/test-offline.sh [command ...]
#   Default command: pytest with branch coverage, then the coverage
#   gate. Example: scripts/test-offline.sh pytest -q tests/test_cli.py
#
# Settings (environment variables):
#   SANDBOX_IMAGE    default: the uv image for .python-version (3.12
#                    if that file is missing)
#   SANDBOX_CPUS     default 2
#   SANDBOX_MEMORY   default 2g
#   SANDBOX_TIMEOUT  seconds for step 2, default 900
set -euo pipefail

cpus="${SANDBOX_CPUS:-2}"
memory="${SANDBOX_MEMORY:-2g}"
timeout_s="${SANDBOX_TIMEOUT:-900}"

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$root"
[ -f uv.lock ] || { echo "uv.lock not found in $root" >&2; exit 2; }

python_version=3.12
if [ -f .python-version ]; then
  python_version="$(cut -d. -f1,2 < .python-version | tr -d '[:space:]')"
fi
image="${SANDBOX_IMAGE:-ghcr.io/astral-sh/uv:python${python_version}-bookworm-slim}"

mkdir -p .sandbox
[ -f .sandbox/.gitignore ] || echo '*' > .sandbox/.gitignore

common=(
  --rm
  --user "$(id -u):$(id -g)"
  --cap-drop=ALL
  --security-opt=no-new-privileges
  --cpus="$cpus" --memory="$memory" --pids-limit=512
  -v "$root:/work" -w /work
  -e HOME=/tmp
  -e UV_PROJECT_ENVIRONMENT=/work/.sandbox/venv
  -e UV_CACHE_DIR=/work/.sandbox/uv-cache
  -e UV_PYTHON_DOWNLOADS=never
  -e UV_LINK_MODE=copy
)

echo "==> Installing locked dependencies (network on)"
docker run "${common[@]}" "$image" sh -c '
  [ -f uv.lock ] || {
    echo "The project is not visible inside Docker. Share its path" \
      "with the Docker VM (Docker Desktop: File sharing; Colima:" \
      "mounts) and retry." >&2
    exit 2
  }
  exec uv sync --locked --quiet'

if [ "$#" -eq 0 ]; then
  set -- sh -c 'pytest -q --cov --cov-branch \
    --cov-report=term-missing --cov-report=json \
    && python scripts/check_coverage.py'
fi

echo "==> Running offline: $*"
docker run "${common[@]}" --network=none "$image" \
  timeout "$timeout_s" uv run --frozen --offline --no-sync "$@"
