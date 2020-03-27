#!/usr/bin/bash
set -euo pipefail

host=nuke@jarvis

echo 'Dumping DB on remote'
ssh $host 'pg_dump -O -F c stickerfinder > stickerfinder.dump'
echo 'Sync DB'
scp $host:stickerfinder.dump ./

echo 'Drop and recreate DB'
dropdb stickerfinder || true
createdb stickerfinder

echo 'Restoring DB'
pg_restore -O -j 4 -F c -d stickerfinder stickerfinder.dump

echo 'Deleting dumps'
rm stickerfinder.dump
ssh $host 'rm stickerfinder.dump'

echo 'Run migrations'
poetry run alembic upgrade head

echo 'Done'
