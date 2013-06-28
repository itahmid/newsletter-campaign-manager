from time import time
from flask import Blueprint, request, redirect, url_for, \
    render_template, session, flash
from pipmail.sql import get_sql, get_rows, insert_row
from pipmail.helpers import login_required, collect_form_errors

mod = Blueprint('newsletters', __name__)


@mod.route('/campaigns', defaults={'page': 0})
@mod.route('/page/<int:page>')
@login_required
def index(page):
    newsletters = get_rows(model='newsletter', page=page)
    return render_template('newsletters/index.html', newsletters=newsletters,
                             page=page)


@mod.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create():
    errors = []
    conn, cur = get_sql()
    cur.execute('SELECT company_id, name FROM company')
    companies = cur.fetchall()
    cur.execute('SELECT first_name, last_name, email FROM staff')
    staff = cur.fetchall()
    if request.method == 'POST':
        form_errors = collect_form_errors(request.form)
        if not form_errors:
            form_items = {}
            for k, v in request.form.iteritems():
                if (v != '' and k[len(k) - 3:] != 'sel'):
                    form_items[k] = v
            form_items['author'] = session.get('current_user')
            form_items['date_added'] = int(time())
            nid = insert_row('newsletter', form_items, conn, cur)
            if not nid:
                return render_template('server_errors.html')
            return redirect(url_for('lists.index', nid=nid))

    return render_template('newsletters/details.html', companies=companies,
                           staff=staff, form_errors=form_errors)


@mod.route('/edit_campaign', methods=['GET', 'POST'])
@login_required
def edit():
    conn, cur = get_sql()

    if request.method == 'GET':
        nid = request.args.get('nid')
        cur.execute('SELECT * FROM `newsletters` WHERE id = %d' % int(nid))
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
            return render_template('newsletters/details.html', newsletter=newsletter,
                                   staff=staff, companies=companies, editing=True,
                                   nid=nid)
        return render_template('error.html', error='lol')

    errors = collect_form_errors(request.form, 'newsletters')
    if not errors:
        try:
            cur.execute("""UPDATE newsletters
                        SET code=%s, subject=%s, author=%s, company=%s,
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
        return redirect(url_for('lists.index', nid=nid))
    return render_template('error.html', error='lol')


@mod.route('/search_campigns/')
@login_required
def search():
    conn, cur = get_sql()
    if request.method == 'POST':
        for k, v in request.form.iteritems():
            print k, v
    return render_template('newsletters/search.html')


@mod.route('/delete_campaign')
@login_required
def delete():
    conn, cur = get_sql()
    cur.execute('DELETE FROM newsletters WHERE id = %d' % nid)
    conn.commit()
    return redirect(url_for('index'))
