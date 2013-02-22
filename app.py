import os, sys
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, _app_ctx_stack, send_from_directory
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

app.secret_key = ''
mysql = MySQL()
app.config.setdefault('MYSQL_DATABASE_PORT', 3306)
app.config.setdefault('MYSQL_DATABASE_USER', 'root')
app.config.setdefault('MYSQL_DATABASE_PASSWORD', '')
app.config.setdefault('MYSQL_DATABASE_DB', '')
app.config.setdefault('MYSQL_DATABASE_CHARSET', 'utf8')
mysql.init_app(app)

error_dict = {'code':'Please enter a campaign code', 
            'replyto_email':'Please enter a reply-to email', 
            'from_email':'Please enter a from email',
             'from_name':'Please enter a from name', 
             'companies_id':'Please enter a company', 
             'subject':'Please enter a subject', 
             'from_name_sel':'','replyto_sel':'','from_email_sel':''
             }

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
    # offset = 15 * page
    # newsletters = newsletters[offset:(offset+15)]

    return render_template('index.html', newsletters=newsletters, page = page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
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

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    error = None
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT companies_id, name FROM `companies`')
    companies = db.fetchall()
    db.execute('SELECT name, email FROM `staff`')
    staff = db.fetchall()

    if request.method == 'POST':
        errors = [opt for opt, val in request.form.iteritems() if val == '']
        if len(errors) > 1:
            error = [error_dict.get(err) for err in errors 
                        if error_dict.get(err) != '']
        else:
            try:
                db.execute("""INSERT INTO newsletters 
                            (name, author, code, date_sent, priority) 
                            VALUES (%s, %s, %s, %s, %s)""",
                            (request.form['subject'], 'John Doe', 
                            request.form['code'], 5, 3)
                            )
                conn.commit()
            except Exception as e:
                print e
                conn.rollback()
            return redirect(url_for('index'))

    return render_template('create_campaign.html', companies=companies, 
                                staff=staff, error=error)

@app.route('/edit_campaign/<int:nid>')
def edit_campaign(nid):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT * FROM `newsletter` WHERE id = %d' % nid)
    res = db.fetchone()
    if res:
        cols = tuple([d[0].decode('utf8') for d in db.description])
        newsletter = dict(zip(cols, res))
        db.execute("""SELECT companies_title 
                        FROM companies 
                        WHERE companies_id = %d""" 
                        % newsletter['companies_id'])
        newsletter['companies_id'] = db.fetchall()[0][0]
        db.execute('SELECT companies_id, companies_title FROM `companies`')
        companies = db.fetchall()
        db.execute('SELECT name, email FROM `staff`')
        staff = db.fetchall()
        return render_template("edit_campaign.html", newsletter=newsletter, 
                                    staff=staff, companies=companies)
    abort(404)

@app.route('/delete_campaign/<int:nid>')
def delete_campaign(nid):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('DELETE FROM newsletter WHERE id = %d' % nid)
    return redirect(url_for('index'))

@app.route('/search/', methods=['POST'])
def search():
    query = request.form['query']

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)