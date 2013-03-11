from functools import wraps
from flask import Flask, redirect, request, url_for, render_template, \
    send_from_directory, session

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session['logged_in']:
            print session['logged_in']
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    return wrapper