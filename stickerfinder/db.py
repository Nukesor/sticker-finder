"""Helper class to get a database engine and to get a session."""
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import case, expression
from sqlalchemy.types import Numeric

from stickerfinder.config import config

engine = create_engine(
    config["database"]["sql_uri"],
    pool_size=config["database"]["connection_count"],
    max_overflow=config["database"]["overflow_count"],
    echo=False,
)
base = declarative_base(bind=engine)


def get_session(connection=None):
    """Get a new db session."""
    session = scoped_session(sessionmaker(bind=engine))
    return session


class greatest(expression.FunctionElement):
    type = Numeric()
    name = "greatest"


@compiles(greatest)
def default_greatest(element, compiler, **kw):
    return compiler.visit_function(element)


@compiles(greatest, "sqlite")
@compiles(greatest, "mssql")
@compiles(greatest, "oracle")
def case_greatest(element, compiler, **kw):
    arg1, arg2 = list(element.clauses)
    return compiler.process(case([(arg1 > arg2, arg1)], else_=arg2), **kw)
