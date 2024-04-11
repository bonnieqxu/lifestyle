from app import app
from functools import wraps
from flask import session
from flask import redirect, url_for

def logged_in(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if session.get("loggedin"):
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))
    return decorated_func