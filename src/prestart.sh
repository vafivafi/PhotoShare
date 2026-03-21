#!/bin/bash
set -e

echo "Run apply migrations.."
cd /app
alembic upgrade head
echo "migrations applied!"

exec "$@"