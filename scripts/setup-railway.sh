#!/usr/bin/env bash
# Idempotent Railway provisioning for Conversion Architect.
#
# Run from the repo root after `railway login`. Safe to re-run.
# Re-running overwrites non-secret vars with the values in this file and
# refreshes the two prompted secrets from stdin / env.
#
# What this does:
#   1. Links to the project (or inits one).
#   2. Adds Redis if it isn't already a service.
#   3. Sets non-secret env vars from this script.
#   4. Prompts for (or reads from env) the two true secrets:
#        - GOOGLE_APPLICATION_CREDENTIALS_JSON
#        - API_KEY
#
# What this deliberately does NOT do:
#   - Generate the GCP service account key (do that with `gcloud` once).
#   - Configure DNS at the registrar.
#   - Deploy (CI does that on push to main).

set -euo pipefail

# ---- config (override via env or CLI flags) ----------------------------------

PROJECT_NAME="${RAILWAY_PROJECT_NAME:-conversion-architect-api}"
API_SERVICE="${API_SERVICE:-conversion-architect-api}"
API_HEALTHCHECK_PATH="${API_HEALTHCHECK_PATH:-/health}"

# Non-secret env vars applied to the API service every run.
declare -A NON_SECRET_VARS=(
  [GA4_MOCK]="false"
  [CORS_ORIGINS]="http://localhost:3000,https://ca-api-production-7266.up.railway.app"
  [RATE_LIMIT_PER_MINUTE]="60"
  [LOG_LEVEL]="INFO"
)

# ---- preflight ---------------------------------------------------------------

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "error: '$1' not installed"; exit 1; }
}

require_cmd railway
require_cmd jq

if ! railway whoami >/dev/null 2>&1; then
  echo "error: not logged in to Railway. Run: railway login"
  exit 1
fi

# ---- 1. link / init ---------------------------------------------------------

echo "==> Linking to Railway project '$PROJECT_NAME'"
if railway status --json >/dev/null 2>&1; then
  echo "    already linked"
else
  railway init --name "$PROJECT_NAME"
fi

# ---- 2. provision redis -----------------------------------------------------

echo "==> Ensuring Redis service exists"
REDIS_EXISTS=$(railway status --json 2>/dev/null \
  | jq -r '.services[]? | select(.name | test("redis"; "i")) | .name' \
  | head -n1 || true)

if [[ -n "${REDIS_EXISTS:-}" ]]; then
  echo "    Redis already provisioned: $REDIS_EXISTS"
else
  railway add --plugin redis
fi

# ---- 3. set non-secret env vars ---------------------------------------------

echo "==> Setting non-secret env vars on API service"
for key in "${!NON_SECRET_VARS[@]}"; do
  railway variables set --service "$API_SERVICE" "$key=${NON_SECRET_VARS[$key]}"
done

# ---- 4. set secrets ---------------------------------------------------------

# API_KEY: generate if not supplied via env.
if [[ -n "${API_KEY:-}" ]]; then
  echo "==> Setting API_KEY from env"
else
  echo "==> Generating API_KEY (32 bytes hex)"
  API_KEY=$(openssl rand -hex 32)
fi
railway variables set --service "$API_SERVICE" "API_KEY=$API_KEY"

# GOOGLE_APPLICATION_CREDENTIALS_JSON: read from file path env var, file arg,
# or stdin. Never commit the JSON to the repo.
GCP_JSON_VALUE=""
if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS_JSON:-}" ]]; then
  GCP_JSON_VALUE="$GOOGLE_APPLICATION_CREDENTIALS_JSON"
elif [[ -n "${GOOGLE_APPLICATION_CREDENTIALS_JSON_FILE:-}" && -f "${GOOGLE_APPLICATION_CREDENTIALS_JSON_FILE}" ]]; then
  GCP_JSON_VALUE="$(cat "${GOOGLE_APPLICATION_CREDENTIALS_JSON_FILE}")"
elif [[ ! -t 0 ]]; then
  GCP_JSON_VALUE="$(cat)"
fi

if [[ -z "$GCP_JSON_VALUE" ]]; then
  echo "warning: GOOGLE_APPLICATION_CREDENTIALS_JSON not provided."
  echo "         export GOOGLE_APPLICATION_CREDENTIALS_JSON_FILE=/path/to/key.json"
  echo "         or pipe the JSON into stdin to set it."
  echo "         The API will run in GA4_MOCK=true mode until a real key is set."
else
  echo "==> Setting GOOGLE_APPLICATION_CREDENTIALS_JSON (truncated for log)"
  railway variables set --service "$API_SERVICE" \
    "GOOGLE_APPLICATION_CREDENTIALS_JSON=$GCP_JSON_VALUE" >/dev/null
  echo "    set"
fi

# ---- 5. wire REDIS_URL into the API service ---------------------------------

echo "==> Wiring REDIS_URL reference variable"
# Railway exposes the Redis plugin's URL as REDIS_URL automatically when both
# services are in the same project. We assert it's visible on the API service.
if railway variables --service "$API_SERVICE" --kv 2>/dev/null | grep -q "^REDIS_URL="; then
  echo "    REDIS_URL already visible to API service"
else
  echo "    note: REDIS_URL not visible yet. If caching fails at runtime,"
  echo "          link the Redis service to the API service in the Railway UI"
  echo "          (Variables -> Shared Variables -> REDIS_URL)."
fi

# ---- summary -----------------------------------------------------------------

cat <<EOF

Done.

Next steps:
  1. Push to main to trigger CI deploy:    git push origin main
  2. Or deploy once manually:              railway up --service $API_SERVICE
  3. Verify health:                        railway run --service $API_SERVICE curl http://localhost:\$PORT/health

API_KEY (save this, shown once):
  $API_KEY

EOF
