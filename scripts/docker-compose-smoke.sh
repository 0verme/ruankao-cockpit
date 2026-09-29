#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  echo "Docker Engine and the Docker Compose plugin are required." >&2
  exit 127
fi

project="ruankao-cockpit-smoke-$$"
test_root="$(mktemp -d)"
export COCKPIT_DATA_DIR="$test_root/data"
export COCKPIT_PORT="$(python3 - <<'PY'
import socket
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
)"
mkdir -p "$COCKPIT_DATA_DIR"
compose=(docker compose --project-name "$project" --file compose.yaml)
base_url="http://127.0.0.1:$COCKPIT_PORT"

cleanup() {
  "${compose[@]}" down --remove-orphans >/dev/null 2>&1 || true
  rm -rf "$test_root"
}
trap cleanup EXIT

wait_for_healthy() {
  local backend_id frontend_id backend_health frontend_health
  for _ in $(seq 1 90); do
    backend_id="$("${compose[@]}" ps --quiet backend 2>/dev/null || true)"
    frontend_id="$("${compose[@]}" ps --quiet frontend 2>/dev/null || true)"
    if [[ -n "$backend_id" && -n "$frontend_id" ]]; then
      backend_health="$(docker inspect --format '{{.State.Health.Status}}' "$backend_id" 2>/dev/null || true)"
      frontend_health="$(docker inspect --format '{{.State.Health.Status}}' "$frontend_id" 2>/dev/null || true)"
      if [[ "$backend_health" == healthy && "$frontend_health" == healthy ]]; then
        return 0
      fi
    fi
    sleep 2
  done
  "${compose[@]}" ps >&2 || true
  "${compose[@]}" logs --no-color >&2 || true
  echo "Timed out waiting for frontend/backend healthchecks." >&2
  return 1
}

check_http_200() {
  local path="$1" status
  status="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' "$base_url$path")"
  if [[ "$status" != 200 ]]; then
    echo "Expected HTTP 200 for $path, got $status" >&2
    return 1
  fi
}

"${compose[@]}" config --quiet
"${compose[@]}" build
"${compose[@]}" up -d
wait_for_healthy
"${compose[@]}" ps

for path in \
  / \
  /learn \
  /learning-units/system-architect-checkin/checkin-001; do
  check_http_200 "$path"
done

curl --fail --silent --show-error \
  "$base_url/api/learning-paths/system-architect-checkin" \
  | python3 -c 'import json,sys; assert json.load(sys.stdin)["path_id"] == "system-architect-checkin"'
curl --fail --silent --show-error \
  "$base_url/api/learning-units/system-architect-checkin/checkin-001" \
  | python3 -c 'import json,sys; assert json.load(sys.stdin)["item_id"] == "checkin-001"'

published_backend_port="$("${compose[@]}" port backend 8000 2>/dev/null || true)"
if [[ -n "$published_backend_port" ]]; then
  echo "Backend unexpectedly published a host port: $published_backend_port" >&2
  exit 1
fi

curl --fail --silent --show-error --request POST "$base_url/api/init" \
  | python3 -c 'import json,sys; assert json.load(sys.stdin)["state"] == "created"'
for filename in config.json progress-events.jsonl review-events.jsonl review-items.json; do
  test -f "$COCKPIT_DATA_DIR/$filename"
done
config_hash="$(sha256sum "$COCKPIT_DATA_DIR/config.json" | cut -d ' ' -f 1)"

"${compose[@]}" down
"${compose[@]}" up -d
wait_for_healthy
"${compose[@]}" ps

test -f "$COCKPIT_DATA_DIR/config.json"
test "$(sha256sum "$COCKPIT_DATA_DIR/config.json" | cut -d ' ' -f 1)" = "$config_hash"
curl --fail --silent --show-error "$base_url/api/today" \
  | python3 -c 'import json,sys; assert "planner" in json.load(sys.stdin)'

echo "Docker Compose build, routing, health, and bind-mount persistence smoke passed."
