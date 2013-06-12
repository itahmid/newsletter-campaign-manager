import os
import time
from flask import Flask, redirect, request, url_for, render_template, \
    send_from_directory, session, Markup
#from flask.ext.mysql import MySQL
import settings
from helpers import login_required
from sql import mysql, get_sql
import simplejson
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'views')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.update(DEBUG=True,)
app.secret_key = settings.secret_key
# from flask.ext.mysql import MySQL
# mysql = MySQL()

app.config.setdefault('MYSQL_DATABASE_PORT', 3306)
app.config.setdefault('MYSQL_DATABASE_USER', settings.USER)
app.config.setdefault('MYSQL_DATABASE_PASSWORD', settings.PASSWORD)
app.config.setdefault('MYSQL_DATABASE_DB', settings.DB)
app.config.setdefault('MYSQL_DATABASE_CHARSET', 'utf8')

mysql.init_app(app)
def to_json(value):
    return Markup(simplejson.dumps(value))

app.jinja_env.filters['to_json'] = to_json


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(
        app.root_path, 'static'), 'ico/favicon.ico')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
@login_required
def index():
    return redirect(url_for('campaigns.index'))

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    errors = []

    if request.method == 'POST' and 'email' in request.form:
        email = request.form.get('email')
        password = request.form.get('password')
        conn, cur = get_sql()
        cur.execute("""SELECT * FROM users WHERE email = '%s'
                    AND password='%s'""" % (email, password))
        check = cur.fetchall()
        if not check:
            errors.append("Invalid email or password")
        else:
            session['logged_in'] = True
            session['current_user'] = email
            cur.execute("""UPDATE users
                           SET last_login=%s
                           WHERE email=%s""", (int(time.time()), email))
            conn.commit()
            return redirect(url_for('campaigns.index'))
    return render_template('auth/login.html', errors=errors)


@app.route('/logout')
@login_required
def logout():
    session['logged_in'] = False
    session['current_user'] = ''
    return render_template('auth/login.html', logout=True)
