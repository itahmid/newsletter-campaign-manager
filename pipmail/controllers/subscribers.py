from flask import Blueprint, request, render_template, redirect, url_for
from werkzeug import secure_filename
from pipmail.helpers import login_required, allowed_file
from pipmail.models import List, Newsletter
from pipmail.sql import get_sql, get_index


import time
import csv
import os

error_dict = {'name': 'Please enter a name for this list',
              'description': 'Please enter a brief description for this list',
              'first_name': 'Please enter a first name for this recipient',
              'last_name': 'Please enter a last name for this recipient',
              'email': 'Please enter an email address for this recipient',
              }

UPLOAD_FOLDER = '%s/pipmail/static/uploads' % os.getcwd()

mod = Blueprint('subscribers', __name__)


@mod.route('/lists', defaults={'page': 0})
@mod.route('/lists/page/<int:page>')
@login_required
def index(page=0, msg=None):
    '''Render subscriber list index'''
    nid = request.args.get('id')
    lists, current_lists = get_index(cntrlr='lists', page=page, id=id)
    return render_template('subscribers/index.html', lists=lists, page=page,
                           nid=nid, msg=msg, current_lists=current_lists)


@mod.route('/create_list', methods=['GET', 'POST'])
@login_required
def create():
    error = None
    conn, cur = get_sql()
    if request.method == 'POST':
        errors = [opt for opt, val in request.form.iteritems()
                  if (val not in ('first_name', 'last_name', 'email')
                      and val == '')]
        if len(errors) > 0:
            error = [error_dict.get(err) for err in errors
                     if error_dict.get(err) != '']
        else:
            try:
                cur.execute("""INSERT into lists(name, description,
                            date_added)
                            VALUES (%s, %s, %s)
                            """, (
                            request.form['name'],
                            request.form['description'],
                            int(time.time())
                            )
                            )
                conn.commit()
                cur.execute('SELECT last_insert_id()')
                lid = cur.fetchall()[0][0]
            except Exception, e:
                conn.rollback()
                error = e
                return render_template('subscribers/details.html', error=error,
                                       editing=False)
            return redirect(url_for('subscribers.edit_list', lid=lid))

    return render_template('subscribers/details.html', error=error,
                           editing=False)


@mod.route('/edit_list/<int:lid>', methods=['GET', 'POST'])
@login_required
def edit(lid):
    conn, cur = get_sql()
    if request.method == 'POST':
        try:
            cur.execute("""UPDATE lists
                           SET name=%s, description=%s
                           WHERE id = %s
                        """, (
                        request.form['name'],
                        request.form['description'],
                        lid)
                        )
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
        return redirect(url_for('subscribers.index'))
    lst = List(conn, cur, lid)
    recips = lst.get_recips()
    if request.method == 'GET':
        edit_name = request.args.get('recip_name')
        if edit_name:
            edit_email = request.args.get('recip_email')
            return render_template('subscribers/details.html', editing=True,
                                   lst=lst, recipients=recips,
                                   edit_name=edit_name, edit_email=edit_email)
        cur.execute("SELECT * FROM recipients")
        res = cur.fetchall()
        cols = tuple([d[0].decode('utf8') for d in cur.description])
        all_recips = [dict(zip(cols, res)) for res in cur]
        return render_template('subscribers/details.html', editing=True,
                               lst=lst, recipients=recips,
                               all_recipients=all_recips)


@mod.route('/delete_list/<int:lid>')
@login_required
def delete(lid):
    conn, cur = get_sql()
    cur.execute('DELETE FROM lists WHERE id = %d' % lid)
    conn.commit()
    return redirect(url_for('subscribers.index'))


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
        return redirect(url_for('subscribers.index', nid=nid))
    return redirect(url_for('subscribers.index'))


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
        return redirect(url_for('subscribers.index', nid=nid))
    return redirect(url_for('subscribers.index'))

