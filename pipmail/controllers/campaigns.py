import time
from flask import Blueprint, request, redirect, url_for, abort, \
    render_template, session
from pipmail import mysql
from pipmail.helpers import login_required, unix_to_local

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
    print session['current_user']
    conn = mysql.get_db()
    cur = conn.cursor()
    offset = 0
    newsletters = []
    if page > 0:
        offset = (page * 15)
    cur.execute("""SELECT * FROM newsletters
                ORDER BY date_added DESC LIMIT 15 OFFSET %s""" % offset)
    cols = tuple([d[0].decode('utf8') for d in cur.description])
    for newsletter in [dict(zip(cols, row)) for row in cur]:
        if newsletter['list_id'] > 0:
            lid = newsletter['list_id']
            cur.execute("""SELECT COUNT(list_id) FROM recipients
                       WHERE list_id = %s""" % lid)
            recip_count = cur.fetchall()
            if recip_count > 0:
                newsletters['list_count'] = recip_count
        else:
            newsletter['list_count'] = 0
        newsletter['date_added'] = unix_to_local(newsletter['date_added'])
        if newsletter['company'] == 0:
            newsletter['company'] = 'N/A'
        else:
            cur.execute("""SELECT name FROM companies
                        WHERE companies_id = %d""" % newsletter['company'])
            newsletter['company'] = cur.fetchall()[0][0]
        newsletters.append(newsletter)
    return render_template('campaigns/index.html', newsletters=newsletters,
                           page=page)


@mod.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    '''Create a new campaign'''
    error = None
    conn = mysql.get_db()
    cur = conn.cursor()
    cur.execute('SELECT companies_id, name FROM `companies`')
    companies = cur.fetchall()
    cur.execute('SELECT name, email FROM `staff`')
    staff = cur.fetchall()
    if request.method == 'POST':
        errors = [opt for opt, val in request.form.iteritems()
                  if (val == '' and opt[len(opt) - 3:] != 'sel')]
        if len(errors) > 1:
            for error in errors:
                print error
            error = [error_dict.get(err) for err in errors
                     if error_dict.get(err) != '']
        else:
            if not request.form.get('unsub'):
                unsub = 0
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
            except Exception, e:
                print e
                conn.rollback()
            return redirect(url_for('index'))

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
                        WHERE newsletters_id = %s
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
            print "ERROR: %s" % e
            conn.rollback()
        return redirect(url_for('index'))
    cur.execute('SELECT * FROM `newsletters` WHERE newsletters_id = %d' % nid)
    res = cur.fetchone()
    if res:
        cols = tuple([d[0].decode('utf8') for d in cur.description])
        newsletter = dict(zip(cols, res))
        cur.execute("""SELECT name
                        FROM companies
                        WHERE companies_id = %d""" % newsletter['company'])
        try:
            newsletter['company'] = cur.fetchall()[0][0]
        except:
            newsletter['company'] = 'None'
        cur.execute('SELECT companies_id, name FROM `companies`')
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
    cur.execute('DELETE FROM newsletters WHERE newsletters_id = %d' % nid)
    conn.commit()
    return redirect(url_for('index'))


# @mod.route('/search/', methods=['POST'])
# def search():
#     query = request.form['query']
