from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug import secure_filename
from pipmail.helpers import login_required, allowed_file, collect_form_errors
from pipmail.models import List, Newsletter
from pipmail.sql import get_sql, get_index, insert_row, update_row, \
    get_companies, get_staff


from time import time
import csv
import os

UPLOAD_FOLDER = '%s/pipmail/static/uploads' % os.getcwd()

mod = Blueprint('lists', __name__)

@mod.route('/lists', defaults={'page': 0})
@mod.route('/lists/page/<int:page>')
@login_required
def index(page=0):
    nid = request.args.get('nid')
    lists = get_index(model='list', page=page)
    return render_template('lists/index.html', lists=lists, page=page, nid=nid)


@mod.route('/create_list', methods=['GET', 'POST'])
@login_required
def create():
    form_errors = None
    conn, cur = get_sql()
    if request.method == 'POST':
        form_errors = collect_form_errors(request.form)
        if not form_errors:
            form_items = {}
            for k, v in request.form.iteritems():
                if (v != ''):
                    form_items[k] = v
            form_items['author'] = session.get('current_user')
            form_items['date_added'] = int(time())
            lid = insert_row('list', form_items, conn, cur)
            if not lid:
                return render_template('server_error.html')
            return redirect(url_for('lists.edit', lid=lid))
    return render_template('lists/details.html', form_errors=form_errors,
                           editing=False)


@mod.route('/edit_list', methods=['GET', 'POST'])
@login_required
def edit():
    conn, cur = get_sql()
    if request.method == 'GET':
        nid = request.args.get('nid')
        lid = request.args.get('lid')
        lst = List(conn, cur, lid).info
        # edit_name = request.args.get('recip_name')
        # if edit_name:
        #     edit_email = request.args.get('recip_email')
        #     return render_template('lists/details.html', editing=True,
        #                            lst=lst, recipients=recips,
        #                            edit_name=edit_name, edit_email=edit_email)
        cur.execute("SELECT * FROM recipient")
        res = cur.fetchall()
        cols = tuple([d[0].decode('utf8') for d in cur.description])
        all_recips = [dict(zip(cols, res)) for res in cur]
        #all_recips = get_rows('recipients', ids
        return render_template('lists/details.html', nid=nid, editing=True,
                               lst=lst, all_recipients=all_recips)

    if request.method == 'POST':
        try:
            cur.execute("""UPDATE lists
                           SET name=%s, description=%s
                           WHERE id = %s
                        """, (
                        request.form['name'],
                        request.form['description'],
                        _id)
                        )
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
        return redirect(url_for('lists.index'))
    lst = List(conn, cur, _id)
    recips = lst.get_recips()


@mod.route('/delete_list/<int:lid>')
@login_required
def delete(lid):
    conn, cur = get_sql()
    cur.execute('DELETE FROM lists WHERE id = %d' % lid)
    conn.commit()
    return redirect(url_for('lists.index'))


@mod.route('/add_to_campaign', methods=['GET', 'POST'])
@login_required
def add_to_campaign():
    conn, cur = get_sql()
    if request.method == 'GET':
        nid = request.args.get('id')
        lid = request.args.get('lid')
        if nid:
            newsletter = Newsletter(conn, cur, nid)
            current_lists = newsletter.list_ids
            if current_lists[0] == '0':
                new_lists = lid
            elif len(current_lists) == 1:
                new_lists = '%s,%s' % (current_lists[0], lid)
                print new_lists
            else:
                print current_lists
                current_lists = ','.join(current_lists)
                
                new_lists = ','.join((current_lists, lid))
               
            try:
                cur.execute("""UPDATE newsletters
                               SET list_ids=%s
                               WHERE id = %s
                            """, (
                            new_lists, nid)
                            )
                conn.commit()
            except Exception as e:
                print(e)
                conn.rollback()
        return redirect(url_for('lists.index', nid=nid))
    return redirect(url_for('lists.index'))


@mod.route('/remove_from_campaign', methods=['GET', 'POST'])
@login_required
def remove_from_campaign():
    conn, cur = get_sql()
    if request.method == 'GET':
        nid = request.args.get('id')
        lid = request.args.get('lid')
        newsletter = Newsletter(conn, cur, nid)
        current_lists = newsletter.list_ids
        if len(current_lists) == 1:
            new_lists = '0'
        else:
            new_lists = current_lists.remove(lid)
            new_lists = ','.join(current_lists)
        try:
            cur.execute("""UPDATE newsletters
                           SET list_ids=%s
                           WHERE id = %s
                        """, (
                        new_lists, nid)
                        )
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
        return redirect(url_for('lists.index', nid=nid))
    return redirect(url_for('lists.index'))