import sqlite3
import MySQLdb
from MySQLdb import cursors

import click
from flask import current_app, g

def connect():
    kwargs = {}

    if current_app.config["MYSQL_HOST"]:
        kwargs["host"] = current_app.config["MYSQL_HOST"]

    if current_app.config["MYSQL_USER"]:
        kwargs["user"] = current_app.config["MYSQL_USER"]

    if current_app.config["MYSQL_PASSWORD"]:
        kwargs["passwd"] = current_app.config["MYSQL_PASSWORD"]

    if current_app.config["MYSQL_DB"]:
        kwargs["db"] = current_app.config["MYSQL_DB"]

    if current_app.config["MYSQL_PORT"]:
        kwargs["port"] = current_app.config["MYSQL_PORT"]

    if current_app.config["MYSQL_UNIX_SOCKET"]:
        kwargs["unix_socket"] = current_app.config["MYSQL_UNIX_SOCKET"]

    if current_app.config["MYSQL_CONNECT_TIMEOUT"]:
        kwargs["connect_timeout"] = current_app.config["MYSQL_CONNECT_TIMEOUT"]

    if current_app.config["MYSQL_READ_DEFAULT_FILE"]:
        kwargs["read_default_file"] = current_app.config["MYSQL_READ_DEFAULT_FILE"]

    if current_app.config["MYSQL_USE_UNICODE"]:
        kwargs["use_unicode"] = current_app.config["MYSQL_USE_UNICODE"]

    if current_app.config["MYSQL_CHARSET"]:
        kwargs["charset"] = current_app.config["MYSQL_CHARSET"]

    if current_app.config["MYSQL_SQL_MODE"]:
        kwargs["sql_mode"] = current_app.config["MYSQL_SQL_MODE"]

    if current_app.config["MYSQL_CURSORCLASS"]:
        kwargs["cursorclass"] = getattr(
            cursors, current_app.config["MYSQL_CURSORCLASS"]
        )

    if current_app.config["MYSQL_AUTOCOMMIT"]:
        kwargs["autocommit"] = current_app.config["MYSQL_AUTOCOMMIT"]

    if current_app.config["MYSQL_CUSTOM_OPTIONS"]:
        kwargs.update(current_app.config["MYSQL_CUSTOM_OPTIONS"])

    return MySQLdb.connect(**kwargs)

def get_db():
    if 'db' not in g:
        # g.db = sqlite3.connect(
        #     current_app.config['DATABASE'],
        #     detect_types=sqlite3.PARSE_DECLTYPES
        # )
        # g.db.row_factory = sqlite3.Row
        g.db=connect()
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        # db.executescript(f.read().decode('utf8'))
        cur = db.cursor()
        cur.execute(f.read().decode('utf8'))
        cur.nextset()
        db.commit()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# def init_app(app):
#     mysql = MySQL(app)
#     app.teardown_appcontext(close_db)
#     app.cli.add_command(init_db_command)

def init_app(app):
    """Initialize the `app` for use with this
    :class:`~flask_mysqldb.MySQL` class.
    This is called automatically if `app` is passed to
    :meth:`~MySQL.__init__`.
    :param flask.Flask app: the application to configure for use with
        this :class:`~flask_mysqldb.MySQL` class.
    """

    app.config.setdefault("MYSQL_HOST", "localhost")
    app.config.setdefault("MYSQL_USER", None)
    app.config.setdefault("MYSQL_PASSWORD", None)
    app.config.setdefault("MYSQL_DB", None)
    app.config.setdefault("MYSQL_PORT", 3306)
    app.config.setdefault("MYSQL_UNIX_SOCKET", None)
    app.config.setdefault("MYSQL_CONNECT_TIMEOUT", 10)
    app.config.setdefault("MYSQL_READ_DEFAULT_FILE", None)
    app.config.setdefault("MYSQL_USE_UNICODE", True)
    app.config.setdefault("MYSQL_CHARSET", "utf8")
    app.config.setdefault("MYSQL_SQL_MODE", None)
    app.config.setdefault("MYSQL_CURSORCLASS", None)
    app.config.setdefault("MYSQL_AUTOCOMMIT", False)
    app.config.setdefault("MYSQL_CUSTOM_OPTIONS", None)

    if hasattr(app, "teardown_appcontext"):
        app.teardown_appcontext(close_db)

    app.cli.add_command(init_db_command)