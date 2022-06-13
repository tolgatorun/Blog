import sqlite3#sqlite is conveinent,no need for separate db server because it is built in to python but each write happens sequintally.

import click
from flask import current_app, g
from flask.cli import with_appcontext

#g is special object and unique for each request.
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(#establishes a connection to DATABASE configuration key
            current_app.config['DATABASE'],#current_app is speacial object that points to Flask application handling request
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row#return rows that behave like dicts
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()#return database connection
    with current_app.open_resource('schema.sql') as f:#open_resource opens a file relative to flaskr package
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')#defining a cl command callet 'init-db' that calls init_db() and shows success message
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

#Since we are using factory function instance isn't available when writing functions.
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)#add a cl command