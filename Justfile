default: run

run:
    poetry run python main.py run

initdb *args:
    poetry run python main.py initdb {{ args }}
    poetry run alembic --config migrations/alembic.ini stamp head

migrate:
    poetry run alembic --config migrations/alembic.ini upgrade head

import-db-dump:
    dropdb -f stickerfinder
    createdb stickerfinder
    pg_restore -O -j 4 -F c -d stickerfinder ./misc/database_dump_2020_07_30.psql_dump

setup:
    poetry install

test:
    #/bin/bash
    createdb stickerfinder_test || echo 'test database exists.'
    poetry run pytest

lint:
    poetry run ruff check ./stickerfinder --show-source
    poetry run ruff format ./stickerfinder --diff

format:
    poetry run ruff check --fix ./stickerfinder
    poetry run ruff format ./stickerfinder

# Watch for something
# E.g. `just watch lint` or `just watch test`
watch *args:
    watchexec --clear 'just {{ args }}'
