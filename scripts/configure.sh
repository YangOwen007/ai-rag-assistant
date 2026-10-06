#!/bin/sh
# Generate the private runtime configuration once; preserve existing deployment settings.
set -eu
cd "$(dirname "$0")/.."
test ! -e .env || { echo 'Root .env already exists; edit it instead.' >&2; exit 1; }
umask 077
printf 'POSTGRES_PASSWORD=%s\nAPP_PORT=3000\nRAG_EMBEDDING_PROVIDER=deterministic\n' "$(openssl rand -hex 32)" > .env
echo 'Created ignored root .env. Run docker compose up --build -d.'
