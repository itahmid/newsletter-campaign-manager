from flask import Blueprint, request, render_template, redirect, url_for
from werkzeug import secure_filename
from pipmail.helpers import (
    login_required,
    allowed_file,
    get_sql
)
from pipmail.models import List, Newsletter


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
def index(page=0):
    '''Render subscriber list index'''
    nid = request.args.get('nid')
    current_lists = []
    conn, cur = get_sql()
    if not nid:
        nid = None
    else:
        current_lists = Newsletter(conn, cur, nid).list_ids
        current_lists = [_id.encode('utf8').replace(',', '') for _id in current_lists]
    offset = 0
    lists = []
    if page > 0:
        offset = (page * 15)
    cur.execute("""SELECT id FROM lists
                ORDER BY date_added
                DESC LIMIT 15 OFFSET %s""" % offset)
    res = cur.fetchall()
    lists = [List(conn, cur, lst[0]) for lst in res]
    for lst in lists:
        print current_lists
        if lst.id in current_lists:
            lst.action = 'remove_from'
        else:
            lst.action = 'add_to'
    return render_template('subscribers/index.html', lists=lists, page=page,
                           nid=nid, current_lists=current_lists)


@mod.route('/create_list', methods=['GET', 'POST'])
@login_required
def create_list():
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
def edit_list(lid):
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


@mod.route('/edit_recipients', methods=['GET', 'POST'])
@login_required
def edit_recipients():
    conn, cur = get_sql()
    if request.method == 'POST':
        lid = request.form.get('list_id')
        if request.form.get('new'):
            first_name = request.form['new_name'].split()[0]
            last_name = request.form['new_name'].split()[1]
            email = request.form['new_email']
            cur.execute("""SELECT *
                           FROM recipients
                           WHERE email = '%s'""" % email)
            res = cur.fetchall()
            if not res:
                try:
                    cur.execute("""INSERT INTO recipients(first_name,
                                last_name, email, list_ids)
                                VALUES (%s,%s,%s,%s)
                                """, (
                                first_name,
                                last_name,
                                email,
                                lid + ','
                                )
                                )
                    conn.commit()
                except Exception, e:
                    print(e)
                    conn.rollback()
                    return redirect(url_for('subscribers.edit_list', lid))
            else:
                return redirect(url_for('subscribers.edit_list'), lid)
        else:
            recip_choice = request.form['recipChoice'].encode('ascii',
                                                              'ignore')
            email = recip_choice.split(',')[1].lstrip()
            if request.form.get('delete'):
                cur.execute("""SELECT id, list_ids
                            FROM recipients
                            WHERE email = '%s'""" % email)
                res = cur.fetchall()
                for i in res:
                    recip_id = i[0]
                    new_list_ids = [_id.encode('utf8')
                                    for _id in i[1].split(',') if _id != lid]
                for x in xrange(15):
                    print new_list_ids
                if len(new_list_ids) > 0:
                    new_list_ids = ','.join(['%s'] * len(new_list_ids))
                else:
                    new_list_ids = '0'
                try:
                    cur.execute("""UPDATE recipients
                                    SET list_ids=%s
                                    WHERE id = %s""",
                                (new_list_ids, recip_id))
                    conn.commit()
                except Exception, e:
                    print(e)
                    conn.rollback()
                return redirect(url_for('subscribers.edit_list', lid=lid))
        if request.form.get('confirm_edit'):
            new_name = request.form['new_name']
            if len(new_name.split()) < 2:
                return redirect(url_for('subscribers.index'))
            first_name = request.form['new_name'].split()[0]
            last_name = request.form['new_name'].split()[1]
            new_email = request.form['new_email']
            old_email = request.form['old_email']
            try:
                cur.execute("""UPDATE recipients
                           SET first_name=%s, last_name=%s, email=%s
                           WHERE email=%s AND list_id = %s""",
                           (first_name, last_name, new_email, old_email, lid))
                conn.commit()
                print "YES"
            except Exception, e:
                print "NO"
                print(e)
                conn.rollback()
            return redirect(url_for('subscribers.edit_list', lid=lid))
        elif request.form.get('edit'):
            recip_info = request.form['recipChoice'].split(',')
            recip_name = recip_info[0]
            recip_email = recip_info[1].lstrip()
            print len(recip_email)
            return redirect(url_for('subscribers.edit_list', lid=lid,
                            recip_sname=recip_name, recip_email=recip_email))
        return redirect(url_for('subscribers.edit_list', lid=lid))


@mod.route('/delete_list/<int:lid>')
@login_required
def delete_campaign(lid):
    conn, cur = get_sql()
    cur.execute('DELETE FROM lists WHERE id = %d' % lid)
    conn.commit()
    return redirect(url_for('subscribers.index'))


@mod.route('/add_to_campaign', methods=['GET', 'POST'])
@login_required
def add_to_campaign():
    conn, cur = get_sql()
    if request.method == 'GET':
        nid = request.args.get('nid')
        lid = request.args.get('lid')
        if nid:
            newsletter = Newsletter(conn, cur, nid)
            current_lists = newsletter.list_ids
            if len(current_lists) > 0:
                current_lists = [_id.encode('utf8').replace(',', '') for _id in current_lists]
                new_lists = current_lists.append(lid)
            else:
                new_lists = '%s,' % lid
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
        nid = request.args.get('nid')
        lid = request.args.get('lid')
        newsletter = Newsletter(conn, cur, nid)
        current_lists = newsletter.list_ids
        if len(current_lists) > 0:
            current_lists = [_id.encode('utf8').replace(',', '') for _id in current_lists]
            new_lists = current_lists.remove(lid)
        else:
            new_lists = '%s,' % lid
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


@mod.route('/upload_csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    conn, cur = get_sql()
    if request.method == 'POST':
        lid = request.form['list_id']
        file = request.files['file']
        if file and allowed_file(file.filename, set(['csv', 'xls', 'xlsx'])):
            filename = secure_filename(file.filename)
            #print os.path.join(UPLOAD_FOLDER, filename)
            try:
                file.save(os.path.join(UPLOAD_FOLDER, filename))
            except Exception as e:
                print e
            ifile = open(os.path.join(UPLOAD_FOLDER, filename), "rb")
            csv_data = csv.reader(ifile)
            header = True
            for row in csv_data:
                if header:
                    header = False
                else:
                    first_name = row[0]
                    last_name = row[1]
                    email = row[2]
                    lid = lid
                    try:
                        cur.execute("""INSERT INTO recipients
                                      (
                                        first_name,
                                        last_name,
                                        email,
                                        list_id
                                      )
                                      VALUES (
                                        %s,
                                        %s,
                                        %s,
                                        %s)
                                    """,
                                   (
                                       first_name,
                                       last_name,
                                       email,
                                       lid
                                   ))
                        conn.commit()
                    except Exception, e:
                        conn.rollback()
                        return redirect(url_for('subscribers.index'))
    return redirect(url_for('subscribers.index'))
