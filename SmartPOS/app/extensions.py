"""
Thin database connection helper.

Repositories call get_db() to get a live PyMySQL connection for the
current request. Flask's `g` object ensures one connection per request,
closed automatically when the request ends.
"""
import pymysql
import pymysql.cursors
from flask import g, current_app
from flask_wtf import CSRFProtect

csrf = CSRFProtect()


def get_db():
    if "db" not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    csrf.init_app(app)
