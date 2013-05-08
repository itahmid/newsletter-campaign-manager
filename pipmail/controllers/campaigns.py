import time
from flask import Blueprint, request, redirect, url_for, abort, \
    render_template, session
from pipmail import mysql
from pipmail.helpers import login_required
from pipmail.models import Newsletter

error_dict = {'code': 'Please enter a campaign code',
              'replyto_email': 'Please enter a reply-to email',
              'from_email': 'Please enter a from email',
              'from_name': 'Please enter a from name',
              'company': 'Please enter a company',
              'subject': 'Please enter a subject',
              }

mod = Blueprint('campaigns', __name__)


@mod.route('/campaigns', defaults={'page': 0})
@mod.route('/page/<int:page>')
@login_required
def index(page):
    '''Render newsletter index'''
    conn = mysql.get_db()
    cur = conn.cursor()
    offset = 0
    newsletters = []
    if page > 0:
        offset = (page * 15)
    cur.execute("""SELECT * FROM newsletters
                ORDER BY date_added
                DESC LIMIT 15 OFFSET %s""" % offset)
    res = cur.fetchall()
    newsletters = [Newsletter(conn, cur, nltr[0]) for nltr in res]
    return render_template('campaigns/index.html', newsletters=newsletters,
                           page=page)


@mod.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    '''Create a new campaign'''
    error = None
    nid = 0
    conn = mysql.get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM companies')
    companies = cur.fetchall()
    cur.execute('SELECT name, email FROM staff')
    staff = cur.fetchall()
    if request.method == 'POST':
        errors = [opt for opt, val in request.form.iteritems()
                  if (val == '' and opt[len(opt) - 3:] != 'sel')]
        if len(errors) > 1:
            error = [error_dict.get(err) for err in errors
                     if error_dict.get(err) != '']
        else:
            unsub = request.form.get('unsub')
            try:
                cur.execute("""INSERT INTO newsletters(code, name, author,
                            company, from_name, from_email, replyto_email,
                            date_added, date_sent, priority, unsub)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """, (
                            request.form['code'],
                            request.form['subject'],
                            session['current_user'],
                            request.form['company'],
                            request.form['from_name'],
                            request.form['from_email'],
                            request.form['replyto_email'],
                            int(time.time()),
                            0,
                            request.form['priority'],
                            unsub
                            )
                            )
                conn.commit()
                cur.execute('SELECT last_insert_id()')
                nid = cur.fetchall()[0][0]
            except Exception, e:
                conn.rollback()
                print "TEST TEST"
                return render_template('error.html', error=e)
            return redirect(url_for('subscribers.index', nid=nid))

    return render_template('campaigns/details.html', companies=companies,
                           staff=staff, error=error, editing=False)


@mod.route('/edit_campaign/<int:nid>', methods=['GET', 'POST'])
@login_required
def edit_campaign(nid):
    '''Edit an existing campaign'''
    conn = mysql.get_db()
    cur = conn.cursor()
    if request.method == 'POST':
        for k, v in request.args.iteritems():
            print k, v
        try:
            cur.execute("""UPDATE newsletters
                        SET code=%s, name=%s, author=%s, company=%s,
                        from_name=%s, from_email=%s, replyto_email=%s,
                        date_added=%s, date_sent=%s, priority=%s, unsub=0
                        WHERE id = %s
                        """, (
                        request.form['code'],
                        request.form['subject'],
                        session['current_user'],
                        request.form['company'],
                        request.form['from_name'],
                        request.form['from_email'],
                        request.form['replyto_email'],
                        int(time.time()),
                        0,
                        request.form['priority'],
                        request.form['unsub'],
                        nid)
                        )
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            return render_template('error.html', error=e)

    cur.execute('SELECT * FROM `newsletters` WHERE id = %d' % nid)
    res = cur.fetchone()
    if res:
        cols = tuple([d[0].decode('utf8') for d in cur.description])
        newsletter = dict(zip(cols, res))
        cur.execute("""SELECT name
                        FROM companies
                        WHERE id = %d""" % newsletter['company'])
        try:
            newsletter['company'] = cur.fetchall()[0][0]
        except:
            newsletter['company'] = 'None'
        cur.execute('SELECT id, name FROM `companies`')
        companies = cur.fetchall()
        cur.execute('SELECT name, email FROM `staff`')
        staff = cur.fetchall()
        return render_template("campaigns/details.html", newsletter=newsletter,
                               staff=staff, companies=companies, editing=True,
                               nid=nid)
    abort(404)


@mod.route('/delete_campaign/<int:nid>')
@login_required
def delete_campaign(nid):
    '''Delete a campaign'''
    conn = mysql.get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM newsletters WHERE id = %d' % nid)
    conn.commit()
    return redirect(url_for('index'))
