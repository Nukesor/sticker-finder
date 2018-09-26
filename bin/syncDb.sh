#!/usr/bin/bash

host=nuke@jarvis

echo 'Dumping DB on remote'
ssh $host 'pg_dump -F c stickerfinder > stickerfinder.dump'
echo 'Sync DB'
scp $host:stickerfinder.dump ./

echo 'Drop and recreate DB'
dropdb stickerfinder || true
createdb stickerfinder

echo 'Restoring DB'
pg_restore -j 4 -F c -d stickerfinder stickerfinder.dump

echo 'Deleting dumps'
rm stickerfinder.dump
ssh $host 'rm stickerfinder.dump'
echo 'Done'
