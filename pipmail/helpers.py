from functools import wraps
from flask import redirect, session
import datetime


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        else:
            return func(*args, **kwargs)
    return wrapper


def unix_to_local(timestamp):
    ts = int(timestamp)
    _time = datetime.datetime.fromtimestamp(
        ts).strftime('%Y-%m-%d %I:%M:%S')
    return _time
