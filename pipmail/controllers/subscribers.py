from flask import Blueprint, request, render_template, redirect, url_for
from werkzeug import secure_filename
from pipmail.helpers import login_required, unix_to_local, allowed_file, get_sql
from pipmail import mysql
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


class List(object):
    '''Model for list'''
    def __init__(self, conn, _id):
        self.conn = conn
        self.cur = conn.cursor()
        self.id = _id
        for k, v in self.get_result_dict().iteritems():
            setattr(self, k, v)
        self.local_time = unix_to_local(self.date_added)
        self.recip_count = self.get_recip_count()

    def get_result_dict(self):
        self.cur.execute("SELECT * FROM lists WHERE id = %s" % self.id)
        res = self.cur.fetchall()
        cols = tuple([d[0].decode('utf8') for d in self.cur.description[1:]])
        return dict(zip(cols, res[0][1:]))

    def get_recip_count(self):
        self.cur.execute("""SELECT COUNT(id)
                            FROM recipients
                            WHERE list_id = %s""" % self.id)
        return self.cur.fetchall()[0][0]

    def get_recips(self):
        self.cur.execute("""SELECT first_name, last_name, email
                            FROM recipients
                            WHERE list_id = %s""" % self.id)
        res = self.cur.fetchall()
        cols = tuple([d[0].decode('utf8') for d in self.cur.description])
        return [dict(zip(cols, res)) for res in self.cur]


@mod.route('/lists', defaults={'page': 0})
@mod.route('/lists/page/<int:page>')
@login_required
def index(page=0):
    '''Render subscriber list index'''
    nid = request.args.get('nid')
    if not nid:
        nid = None
    conn = mysql.get_db()
    cur = conn.cursor()
    offset = 0
    lists = []
    if page > 0:
        offset = (page * 15)
    cur.execute("""SELECT id FROM lists
                ORDER BY date_added
                DESC LIMIT 15 OFFSET %s""" % offset)
    res = cur.fetchall()
    lists = [List(conn, lst[0]) for lst in res]
    return render_template('subscribers/index.html', lists=lists, page=page,
                           nid=nid)

# def form_errors(rform, cntrlr):
#     errors = [opt for opt, val in rform.iteritems()
#               if (vaerror_dict.get(cntrlr)


@mod.route('/create_list', methods=['GET', 'POST'])
@login_required
def create_list():
    error = None
    conn, cur = get_sql(mysql)
    if request.method == 'POST':
        errors = [opt for opt, val in request.form.iteritems()
                  if (val not in ('first_name', 'last_name', 'email')
                      and val == '')]
        if len(errors) > 0:
            error = [error_dict.get(err) for err in errors
                     if error_dict.get(err) != '']
        else:
            try:
                cur.execute("""INSERT into lists (name, description,
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
    conn, cur = get_sql(mysql)

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

    lst = List(conn, lid)
    recips = lst.get_recips()
    if request.method == 'GET':
        edit_name = request.args.get('recip_name')
        edit_email = request.args.get('recip_email')
        return render_template('subscribers/details.html', editing=True,
                               lst=lst, recipients=recips,
                               edit_name=edit_name, edit_email=edit_email)
    return render_template('subscribers/details.html', editing=True,
                           lst=lst, recipients=recips)


@mod.route('/edit_recipients', methods=['GET', 'POST'])
@login_required
def edit_recipients():
    conn, cur = get_sql(mysql)
    if request.method == 'POST':
        lid = request.form.get('list_id')
        if request.form.get('new'):
            first_name = request.form['new_name'].split()[0]
            last_name = request.form['new_name'].split()[1]
            email = request.form['new_email']
            print email
            print len(email)
            cur.execute("""SELECT *
                           FROM recipients
                           WHERE email = '%s'""" % email)
            res = cur.fetchall()
            if not res:
                try:
                    cur.execute("""INSERT INTO recipients(first_name,
                                last_name, email, list_id)
                                VALUES (%s,%s,%s,%s)
                                """, (
                                first_name,
                                last_name,
                                email,
                                lid
                                )
                                )
                    conn.commit()
                except Exception, e:
                    print(e)
                    conn.rollback()
                    return redirect(url_for('subscribers.index'))
            else:
                return render_template('subscribers/lists', error="error lol")
        else:
            recip_choice = request.form['recipChoice'].encode('ascii',
                                                              'ignore')
            email = recip_choice.split(',')[1].lstrip()
            if request.form.get('delete'):
                try:
                    cur.execute("""DELETE FROM recipients
                                WHERE list_id = %s
                                AND email = '%s'""" % (lid, email))
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
                            recip_name=recip_name, recip_email=recip_email))
        return redirect(url_for('subscribers.index'))


@mod.route('/delete_list/<int:lid>')
@login_required
def delete_campaign(lid):
    conn, cur = get_sql(mysql)
    cur.execute('DELETE FROM lists WHERE id = %d' % lid)
    conn.commit()
    return redirect(url_for('subscribers.index'))


@mod.route('/add_to_campaign', methods=['GET', 'POST'])
@login_required
def add_to_campaign():
    nid = request.args.get('nid')
    lid = request.args.get('lid')
    conn = mysql.get_db()
    cur = conn.cursor()
    if request.method == 'GET':
        try:
            cur.execute("""UPDATE newsletters
                           SET list_id=%s
                           WHERE id = %s
                        """, (
                        lid, nid)
                        )
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
    return redirect(url_for('subscribers.index'))


@mod.route('/upload_csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    conn, cur = get_sql(mysql)
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
