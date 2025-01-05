import sqlite3

from flask import redirect, session, g
from functools import wraps

DATABASE = "trackapp.db"

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def get_db():
    """
    Get a databse connection for the current request context.
    Creates a connection if one does not already exist.
    """

    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(error=None):
    """
    Close the databse connection for the current request context, if it exists.
    """

    db = g.pop("db", None)
    if db is not None:
        db.close()

def time_elapsed(s):
    """
    Converts seconds into various time formats
    """
    s = float(s)
    if s >= 3600:
        h = s // 3600
        m = (s % 3600) // 60
        s = s % 60
        return f"{h:.0f}h {m:02.0f}m {s:02.0f}s"

    elif s >= 60:
        m = s // 60
        s = s % 60
        return f"{m:02.0f}m {s:02.0f}s"

    else:
        return f"{s:.0f}s"

def distance_conv(m):
    """
    Converts metres into kilometres
    """

    if m >= 1000:
        return f"{(m / 1000):.2f}km"
    else:
        return f"{m}m"

def pace_calc(x, y):
    """
    Calculates pace from x (seconds) and y (metres)
    """
    sec_per_km = x / (y / 1000)
    minutes = int(sec_per_km // 60)
    remainder = int(sec_per_km % 60)

    return f"{minutes}:{remainder:02d}"


