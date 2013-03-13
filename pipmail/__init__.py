import os
from flask import Flask, redirect, request, url_for, render_template, \
    send_from_directory, session
from flask.ext.mysql import MySQL
import settings
from helpers import login_required, unix_to_local
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


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
@login_required
def index(page):
    conn = mysql.get_db()
    db = conn.cursor()
    # db.execute('SELECT COUNT(newsletters_id) FROM newsletters')
    # count = db.fetchall()
    db.execute("""SELECT * FROM `newsletters`
                ORDER BY date_added DESC LIMIT 15 OFFSET %s""" % page)
    cols = tuple([d[0].decode('utf8') for d in db.description])
    _newsletters = [dict(zip(cols, row)) for row in db]
    newsletters = []
    for newsletter in _newsletters:

        newsletter['date_added'] = unix_to_local(newsletter['date_added'])
        if newsletter['company'] == 0:
            newsletter['company'] = 'N/A'
        else:
            db.execute("""SELECT name FROM `companies`
                        WHERE companies_id = %d""" % newsletter['company'])
            newsletter['company'] = db.fetchall()[0][0]
        newsletters.append(newsletter)

    return render_template('index.html', newsletters=newsletters, page=page)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        password = request.form['password']
        db = mysql.get_db().cursor()
        db.execute("""SELECT * FROM users WHERE name = '%s'
                    AND password='%s'""" % (username, password))
        check = db.fetchall()
        if not check:
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('auth/login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session['logged_in'] = False
    return render_template('auth/login.html', logout=True)
