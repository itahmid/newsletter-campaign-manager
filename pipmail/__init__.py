import os
from flask import Flask, redirect, request, url_for, render_template, \
    send_from_directory, session
from flask.ext.mysql import MySQL
import settings
from helpers import login_required
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'views')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.update(DEBUG=True,)
app.secret_key = settings.secret_key
mysql = MySQL()


app.config.setdefault('MYSQL_DATABASE_PORT', 3306)
app.config.setdefault('MYSQL_DATABASE_USER', settings.USER)
app.config.setdefault('MYSQL_DATABASE_PASSWORD', settings.PASSWORD)
app.config.setdefault('MYSQL_DATABASE_DB', settings.DB)
app.config.setdefault('MYSQL_DATABASE_CHARSET', 'utf8')

mysql.init_app(app)


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        password = request.form['password']
        cur = mysql.get_db().cursor()
        cur.execute("""SELECT * FROM users WHERE name = '%s'
                    AND password='%s'""" % (username, password))
        check = cur.fetchall()
        if not check:
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            session['current_user'] = username
            return redirect(url_for('campaigns.index'))
    return render_template('auth/login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session['logged_in'] = False
    session['current_user'] = ''
    return render_template('auth/login.html', logout=True)
