#!/bin/env python
"""Drop and create a new database with schema."""

from sqlalchemy_utils.functions import database_exists, create_database, drop_database
from stickerfinder.db import engine, base
from stickerfinder.models import * # noqa


db_url = engine.url
if database_exists(db_url):
    drop_database(db_url)
create_database(db_url)

with engine.connect() as con:
    con.execute('CREATE EXTENSION pg_trgm;')


base.metadata.drop_all()
base.metadata.create_all()
