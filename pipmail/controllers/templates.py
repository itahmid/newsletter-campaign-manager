from flask import Blueprint, render_template, request, session, redirect, url_for
from pipmail.sql import get_sql, get_index, insert_row, update_row, \
    get_companies, get_staff
from pipmail.helpers import login_required, allowed_file, collect_form_errors
from pipmail.models import Template
from time import time
import csv
import os

mod = Blueprint('templates', __name__)


@mod.route('/templates', defaults={'page': 0})
@mod.route('/page/<int:page>')
def index(page):
    nid = request.args.get('nid')
    templates = get_index(model='template', page=page)
    return render_template('templates/index.html', templates=templates)

@mod.route('/create_template', methods=['POST', 'GET'])
@login_required
def create():
    nid = request.args.get('nid')
    form_errors = None
    conn, cur = get_sql()
    if request.method == 'POST':
        form_errors = collect_form_errors(request.form)
        if not form_errors:
            form_items = {}
            for k, v in request.form.iteritems():
                if (k == 'editor1'):
                    form_items['html'] = request.form['editor1']
                else:
                    form_items[k] = v
            form_items['author'] = session.get('current_user')
            form_items['date_added'] = int(time())
            tid = insert_row('template', form_items, conn, cur)
            if not tid:
                return render_template('server_error.html')
            return redirect(url_for('templates.edit', nid=nid, tid=tid))
    return render_template('template/details.html', nid=nid, error=error)

@mod.route('/edit_template', methods=['GET'])
@login_required
def edit():
    conn, cur = get_sql()
    if request.method == 'GET':
        nid = request.args.get('nid')
        tid = request.args.get('tid')
        tmplt = Template(conn, cur, tid).info
        return render_template('templates/details.html', nid=nid, tid=tid, tmplt=tmplt)

# @mod.route('/create_template', methods=['GET', 'POST'])
# @login_required
# def create_template():
#     '''Create a new template'''
#     errors = None
#     conn, cur = get_sql()
#     if request_method == 'POST':
#         errors = collect_form_errors(request.form, 'campaigns')
#         if not errors:
#             try:
#                 cur.execute("""INSERT INTO newsletters(code, name, author,
#                             company, from_name, from_email, replyto_email,
#                             date_added, date_sent, priority, unsub)
#                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#                             """, (
#                             request.form.get('code'),
#                             request.form.get('subject'),
#                             session.get('current_user'),
#                             request.form.get('company'),
#                             request.form.get('from_name'),
#                             request.form.get('from_email'),
#                             request.form.get('replyto_email'),
#                             int(time.time()),
#                             0,
#                             request.form.get('priority'),
#                             request.form.get('unsub', 0),
#                             )
#                             )
#                 conn.commit()
#                 cur.execute('SELECT last_insert_id()')
#                 nid = cur.fetchall()[0][0]
#             except Exception, err:
#                 conn.rollback()
#                 return render_template('error.html', error=err)
#             return redirect(url_for('subscribers.index', nid=nid))

#     return render_template('campaigns/details.html', companies=companies,
#                            staff=staff, errors=errors, editing=False)