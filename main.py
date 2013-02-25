import os, sys
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, _app_ctx_stack, send_from_directory
from flaskext.mysql import MySQL
import settings

app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

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
    return send_from_directory(os.path.join(app.root_path, 'static'), 
                                                'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT COUNT(id) FROM newsletter')
    count = db.fetchall()
    db.execute("""SELECT * from `newsletter` 
                ORDER BY date_added DESC LIMIT 15 OFFSET %s""" % page)
    cols = tuple([d[0].decode('utf8') for d in db.description])
    _newsletters = [dict(zip(cols, row)) for row in db]
    newsletters = []
    for newsletter in _newsletters:
        db.execute("""SELECT companies_title 
                    FROM companies 
                    WHERE companies_id = %d""" 
                    % newsletter['companies_id'])
        newsletter['companies_id'] = db.fetchall()[0][0]
        newsletters.append(newsletter)

    return render_template('index.html', newsletters=newsletters, page= page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = mysql.get_db().cursor()
        db.execute("""SELECT * FROM user WHERE user_name = '%s' 
                    AND user_password='%s'""" % (username, password))
        check = db.fetchall()
        if not check:
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            return redirect(url_for('index'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    from controllers import campaigns
    app.register_blueprint(campaigns.mod)
    app.run(host='0.0.0.0', port = 5000, debug = True)