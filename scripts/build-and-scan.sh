#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <dockerfile-path> <sanitized-name>"
  exit 2
fi

path="$1"
name="$2"
ROOT_DIR="$(pwd)"

mkdir -p "${ROOT_DIR}/trivy-reports"

ctx=$(dirname "$path")
tag="local/${name}:ci"

echo "Building $path (context: $ctx) -> $tag"
if ! docker build -t "$tag" -f "$path" "$ctx"; then
  echo "[ERROR] docker build failed for $path"
  exit 3
fi

echo "Scanning $tag (JSON -> trivy-reports/${name}.json)"
# Save full JSON report (do not fail if Trivy finds vulnerabilities)
if ! docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "${ROOT_DIR}/trivy-reports":/reports aquasec/trivy image --format json -o "/reports/${name}.json" "$tag"; then
  echo "[WARN] Trivy JSON scan failed or returned non-zero status for $tag"
fi

echo "Summary (CRITICAL/HIGH):"
# Print human-readable table of CRITICAL/HIGH
if ! docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --format table --severity CRITICAL,HIGH "$tag"; then
  echo "[WARN] Trivy table scan failed or returned non-zero status for $tag"
fi

exit 0
