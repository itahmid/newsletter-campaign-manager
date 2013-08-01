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

mod = Blueprint('recipients', __name__)


@mod.route('/create', methods=['GET', 'POST'])
@login_required
def create_recipient():
    conn, cur = get_sql()
    if request.method == 'POST':
        lid = request.form.get('list_id')
        first_name = request.form['new_first_name']
        last_name = request.form['new_last_name']
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
    return redirect(url_for('lists.edit', lid=lid))


@mod.route('/remove', methods=['GET', 'POST'])
@login_required
def remove():
    conn, cur = get_sql()
    if request.method == 'POST':
        lid = request.form.get('list_id')
        cur.execute("""SELECT id, list_ids
                        FROM recipients
                        WHERE email = '%s'""" % email)
        res = cur.fetchall()
        for i in res:
            recip_id = i[0]
            new_list_ids = [_id.encode('utf8')
                            for _id in i[1].split(',') if _id != lid]
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
    return redirect(url_for('lists.edit', lid=lid))


@mod.route('/edit_recipient', methods=['GET', 'POST'])
@login_required
def edit():
    new_name = request.form.get('new_name')
    if len(new_name.split()) < 2:
        return redirect(url_for('lists.index'))
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
    except Exception, e:
        print(e)
        conn.rollback()
        return redirect(url_for('lists.edit', lid=lid))


# @mod.route('/upload_csv', methods=['GET', 'POST'])
# @login_required
# def upload_csv():
#     conn, cur = get_sql()
#     if request.method == 'POST':
#         lid = request.form['list_id']
#         file = request.files['file']
#         if file and allowed_file(file.filename, set(['csv', 'xls', 'xlsx'])):
#             filename = secure_filename(file.filename)
#             #print os.path.join(UPLOAD_FOLDER, filename)
#             try:
#                 file.save(os.path.join(UPLOAD_FOLDER, filename))
#             except Exception as e:
#                 print e
#             ifile = open(os.path.join(UPLOAD_FOLDER, filename), "rb")
#             csv_data = csv.reader(ifile)
#             header = True
#             for row in csv_data:
#                 if header:
#                     header = False
#                 else:
#                     first_name = row[0]
#                     last_name = row[1]
#                     email = row[2]
#                     lid = lid
#                     try:
#                         cur.execute("""INSERT INTO recipients
#                                       (
#                                         first_name,
#                                         last_name,
#                                         email,
#                                         list_id
#                                       )
#                                       VALUES (
#                                         %s,
#                                         %s,
#                                         %s,
#                                         %s)
#                                     """,
#                                    (
#                                        first_name,
#                                        last_name,
#                                        email,
#                                        lid
#                                    ))
#                         conn.commit()
#                     except Exception, e:
#                         conn.rollback()
#                         return redirect(url_for('subscribers.index'))
#     return redirect(url_for('subscribers.index'))