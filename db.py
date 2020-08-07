import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

#Create tables in db
def create_tables():
    db.create_all()

#Connect to database
def conn_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

#Close database
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#Initialize application from the server file. This is used to map to the application
def initialize_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(initial_db_command)

#Add a command that will run the script
@click.command('inititialize-db')
@with_appcontext
def initial_db_command():
    """Clear the existing data and create new tables."""
    initialize_db()
    click.echo('Initialized the database.')

#Initialize DB
def initialize_db():
    db = conn_db()
    with current_app.open_resource('Model.sql') as f:
        db.executescript(f.read().decode('utf8'))