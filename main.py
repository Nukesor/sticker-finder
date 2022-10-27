#!/bin/env python
"""The main entry point for the stickerfinder."""
from contextlib import contextmanager

import typer
from sqlalchemy_utils.functions import database_exists, create_database, drop_database

from stickerfinder.config import config
from stickerfinder.db import engine, base
from stickerfinder.models import *  # noqa
from stickerfinder.stickerfinder import init_app

cli = typer.Typer()


@contextmanager
def wrap_echo(msg: str):
    typer.echo(f"{msg}... ", nl=False)
    yield
    typer.echo("done.")


@cli.command()
def initdb(exist_ok: bool = False, drop_existing: bool = False):
    """Set up the database.

    Can be used to remove an existing database.
    """
    db_url = engine.url
    typer.echo(f"Using database at {db_url}")

    if database_exists(db_url):
        if drop_existing:
            with wrap_echo("Dropping database"):
                drop_database(db_url)
        elif not exist_ok:
            typer.echo(
                "Database already exists, aborting.\n"
                "Use --exist-ok if you are sure the database is uninitialized and contains no data.\n"
                "Use --drop-existing if you want to recreate it.",
                err=True,
            )
            return

    with wrap_echo("Creating database"):
        create_database(db_url)
        pass

    with engine.connect() as con:
        with wrap_echo("Installing extensions"):
            con.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
            con.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            pass

    with wrap_echo("Creating metadata"):
        base.metadata.create_all()
        pass

    typer.echo("Database initialization complete.")


@cli.command()
def run():
    """Actually start the bot."""
    updater = init_app()

    if config["webhook"]["enabled"]:
        typer.echo("Starting the bot in webhook mode.")
        updater.start_webhook(
            listen="127.0.0.1",
            port=config["webhook"]["port"],
            url_path=config["webhook"]["token"],
        )
        domain = config["webhook"]["domain"]
        token = config["webhook"]["token"]
        print("Starting up")
        updater.bot.set_webhook(
            url=f"{domain}{token}",
            certificate=open(config["webhook"]["cert_path"], "rb"),
        )
    else:
        typer.echo("Starting the bot in polling mode.")
        updater.start_polling()
        print("Starting up")
        updater.idle()


if __name__ == "__main__":
    cli()

#!/bin/env python
"""Start the bot."""
