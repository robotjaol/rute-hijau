#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "==> Install engine dependencies"
cd "$ROOT/engine"
pip install -r requirements.txt -q

echo "==> Install web dependencies"
cd "$ROOT/web"
npm install --silent

if [ ! -f "$ROOT/web/.env.local" ]; then
  echo "NEXT_PUBLIC_ENGINE_URL=http://localhost:8000" > "$ROOT/web/.env.local"
  echo "==> Created web/.env.local"
fi

cleanup() {
  echo ""
  echo "==> Stopping servers..."
  kill "$ENGINE_PID" 2>/dev/null || true
  kill "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "==> Starting engine on http://localhost:8000"
cd "$ROOT/engine"
uvicorn app:app --port 8000 &
ENGINE_PID=$!

echo "==> Starting web on http://localhost:3000"
cd "$ROOT/web"
npm run dev &
WEB_PID=$!

echo ""
echo "  Engine : http://localhost:8000"
echo "  Web    : http://localhost:3000"
echo ""
echo "  Tekan Ctrl+C untuk berhenti."
echo ""

wait "$WEB_PID"
