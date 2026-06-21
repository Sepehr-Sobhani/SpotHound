#!/usr/bin/env bash
# Build and start the full stack, then seed the admin user + spots.
# Run on the server, from the repo root, after creating .env.prod.
set -euo pipefail
cd "$(dirname "$0")"

COMPOSE="docker compose --env-file .env.prod -f docker-compose.prod.yml"

if [ ! -f .env.prod ]; then
  echo "Missing .env.prod — copy .env.prod.example to .env.prod and fill it in."
  exit 1
fi

echo "Building and starting containers..."
$COMPOSE up -d --build

echo "Waiting for the database..."
until $COMPOSE exec -T db pg_isready -U spothound >/dev/null 2>&1; do sleep 2; done

echo "Seeding admin user + spots..."
$COMPOSE exec -T backend python -m app.seed

echo
echo "Deployed. Open the app at your SITE_ADDRESS (http://<server-ip>/ by default)."
echo "Log in with ADMIN_USERNAME / ADMIN_PASSWORD from .env.prod."
