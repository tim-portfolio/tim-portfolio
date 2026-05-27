#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist-cn"
PROJECT_NAME="${EDGEONE_PROJECT_NAME:-tim-portfolio}"
ENVIRONMENT="${EDGEONE_ENVIRONMENT:-production}"
AREA="${EDGEONE_AREA:-global}"
TOKEN_FILE="${EDGEONE_TOKEN_FILE:-$ROOT/.edgeone/.Token}"
NPM_CONFIG_CACHE="${NPM_CONFIG_CACHE:-$ROOT/.npm-cache}"
EDGEONE_CLI="$ROOT/.edgeone/cli/node_modules/.bin/edgeone"
export NPM_CONFIG_CACHE

mode="${1:-deploy}"

if [[ -z "${EDGEONE_API_TOKEN:-}" && -f "$TOKEN_FILE" ]]; then
  EDGEONE_API_TOKEN="$(tr -d '\r\n' < "$TOKEN_FILE")"
fi

if [[ -z "${EDGEONE_API_TOKEN:-}" ]]; then
  echo "Missing EdgeOne token. Set EDGEONE_API_TOKEN or create $TOKEN_FILE." >&2
  exit 1
fi

python3 "$ROOT/scripts/build_cn_release.py"

if [[ ! -f "$DIST/index.html" ]]; then
  echo "Build failed: $DIST/index.html not found." >&2
  exit 1
fi

echo "EdgeOne project: $PROJECT_NAME"
echo "Deploy source: $DIST"
echo "Token source: ${EDGEONE_API_TOKEN:+configured}"

if [[ "$mode" == "--check" || "$mode" == "check" ]]; then
  echo "Check complete. Run scripts/deploy_edgeone.sh to deploy."
  exit 0
fi

if [[ ! -x "$EDGEONE_CLI" ]]; then
  npm --cache "$NPM_CONFIG_CACHE" install --prefix "$ROOT/.edgeone/cli" edgeone@1.5.4
fi

"$EDGEONE_CLI" pages deploy "$DIST" \
  --name "$PROJECT_NAME" \
  --token "$EDGEONE_API_TOKEN" \
  --env "$ENVIRONMENT" \
  --area "$AREA"
