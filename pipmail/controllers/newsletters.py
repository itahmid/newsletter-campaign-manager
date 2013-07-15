from time import time
from flask import Blueprint, request, redirect, url_for, \
    render_template, session, flash
from pipmail.sql import get_sql, get_index, insert_row, update_row, \
    get_companies, get_staff
from pipmail.helpers import login_required, collect_form_errors

mod = Blueprint('newsletters', __name__)


@mod.route('/campaigns', defaults={'page': 0})
@mod.route('/page/<int:page>')
@login_required
def index(page):
    newsletters = get_index(model='newsletter', page=page)
    return render_template('newsletters/index.html', newsletters=newsletters,
                             page=page)


@mod.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create():
    form_errors = None
    conn, cur = get_sql()
    companies = get_companies(conn, cur)
    staff = get_staff(conn, cur)
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
                return render_template('server_error.html')
            return redirect(url_for('lists.index', nid=nid))

    return render_template('newsletters/details.html', companies=companies,
                           staff=staff, form_errors=form_errors)


@mod.route('/edit_campaign', methods=['GET', 'POST'])
@login_required
def edit():
    form_errors = None
    conn, cur = get_sql()
    companies = get_companies(conn, cur)
    staff = get_staff(conn, cur)
    if request.method == 'GET':
        nid = request.args.get('nid')
        cur.execute('SELECT * FROM `newsletter` WHERE newsletter_id = %d' % int(nid))
        res = cur.fetchone()
        if res:
            cols = tuple([d[0].decode('utf8') for d in cur.description])
            newsletter = dict(zip(cols, res))
            company_name = cur.execute("""SELECT name 
                                          FROM company 
                                          WHERE company_id = %d""" % int(newsletter['company']))
            comp_name = cur.fetchone()[0]
            newsletter['company'] = (newsletter['company'], comp_name)
            return render_template('newsletters/details.html', newsletter=newsletter,
                                   staff=staff, companies=companies, nid=nid)
        return render_template('404.html')
    if request.method == 'POST':    
        nid = request.args.get('nid')
        form_errors = collect_form_errors(request.form)
        if not form_errors:
            form_items = {}
            for k, v in request.form.iteritems():
                if (v != '' and k[len(k) - 3:] != 'sel'):
                    form_items[k] = v
            form_items['date_added'] = int(time())
            nid = update_row('newsletter', form_items, conn, cur, nid)
            if not nid:
                return render_template('server_error.html')
            return redirect(url_for('lists.index', nid=nid))
        return render_template('newsletters/details.html', newsletter=newsletter,
                                staff=staff, companies=companies, nid=nid, 
                                form_errors=form_errors)


@mod.route('/search_campigns/')
@login_required
def search():
    conn, cur = get_sql()
    if request.method == 'POST':
        for k, v in request.form.iteritems():
            print k, v
    return render_template('newsletters/search.html')


@mod.route('/delete_campaign', methods=['GET'])
@login_required
def delete():
    if request.method == 'GET':
        conn, cur = get_sql()
        cur.execute('DELETE FROM newsletter WHERE newsletter_id = %s' % nid)
        conn.commit()
        return redirect(url_for('index'))
