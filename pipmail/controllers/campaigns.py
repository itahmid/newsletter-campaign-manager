import time
from flask import Blueprint, request, redirect, url_for, \
    render_template, session
from pipmail.sql import get_sql, get_index
from pipmail.helpers import login_required, collect_form_errors


mod = Blueprint('campaigns', __name__)


@mod.route('/campaigns', defaults={'page': 0})
@mod.route('/page/<int:page>')
@login_required
def index(page):
    '''Render newsletter index'''
    newsletters = get_index(cntrlr='newsletters', page=page)
    return render_template('campaigns/index.html', newsletters=newsletters,
                           page=page)


@mod.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    '''Create a new campaign'''
    errors = None
    conn, cur = get_sql()
    cur.execute('SELECT id, name FROM companies')
    companies = cur.fetchall()
    cur.execute('SELECT name, email FROM staff')
    staff = cur.fetchall()
    if request.method == 'POST':
        errors = collect_form_errors(request.form, 'campaigns')
        if not errors:
            try:
                cur.execute("""INSERT INTO newsletters(code, name, author,
                            company, from_name, from_email, replyto_email,
                            date_added, date_sent, priority, unsub)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """, (
                            request.form.get('code'),
                            request.form.get('subject'),
                            session.get('current_user'),
                            request.form.get('company'),
                            request.form.get('from_name'),
                            request.form.get('from_email'),
                            request.form.get('replyto_email'),
                            int(time.time()),
                            0,
                            request.form.get('priority'),
                            request.form.get('unsub', 0),
                            )
                            )
                conn.commit()
                cur.execute('SELECT last_insert_id()')
                nid = cur.fetchall()[0][0]
            except Exception, err:
                conn.rollback()
                return render_template('error.html', error=err)
            return redirect(url_for('subscribers.index', nid=nid))

    return render_template('campaigns/details.html', companies=companies,
                           staff=staff, errors=errors, editing=False)


@mod.route('/edit_campaign/<int:nid>', methods=['GET', 'POST'])
@login_required
def edit_campaign(nid):
    '''Edit an existing campaign'''
    conn, cur = get_sql()
    if request.method == 'POST':
        errors = collect_form_errors(request.form, 'campaigns')
        if not errors:
            try:
                cur.execute("""UPDATE newsletters
                            SET code=%s, name=%s, author=%s, company=%s,
                            from_name=%s, from_email=%s, replyto_email=%s,
                            date_added=%s, date_sent=%s, priority=%s, unsub=%s
                            WHERE id = %s
                            """, (
                            request.form.get('code'),
                            request.form.get('subject'),
                            session.get('current_user'),
                            request.form.get('company'),
                            request.form.get('from_name'),
                            request.form.get('from_email'),
                            request.form.get('replyto_email'),
                            int(time.time()),
                            0,
                            request.form.get('priority'),
                            request.form.get('unsub', 0),
                            nid)
                            )
                conn.commit()
            except Exception as err:
                conn.rollback()
                return render_template('error.html', error=err)
            return redirect(url_for('subscribers.index', nid=nid))
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


@mod.route('/delete_campaign/<int:nid>')
@login_required
def delete_campaign(nid):
    '''Delete a campaign'''
    conn, cur = get_sql()
    cur.execute('DELETE FROM newsletters WHERE id = %d' % nid)
    conn.commit()
    return redirect(url_for('index'))
