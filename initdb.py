#!/bin/env python
"""Drop and create a new database with schema."""

from sqlalchemy_utils.functions import database_exists, create_database
from stickerfinder.db import engine, base
from stickerfinder.models import * # noqa

db_url = engine.url
if not database_exists(db_url):
    create_database(db_url)

    with engine.connect() as con:
        con.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')

    base.metadata.create_all()
