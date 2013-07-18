from functools import wraps
from flask import redirect, session, flash, url_for
import datetime


def allowed_file(filename, exts):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in exts


def collect_form_errors(form):
    form_errors = []
    for k, v in form.iteritems():
        if (v == '' and k[len(k) - 3:] != 'sel'):
            form_errors.append(k.replace('_', ' '))
    return form_errors

def collect_form_items(form):
    return 'lol'
    

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
