from flask import Blueprint, request, render_template, redirect, url_for
from werkzeug import secure_filename
from pipmail.helpers import login_required, unix_to_local
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

ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx'])
UPLOAD_FOLDER = '%s/pipmail/static/uploads' % os.getcwd()


mod = Blueprint('subscribers', __name__)


@mod.route('/lists', defaults={'page': 0})
@mod.route('/lists/page/<int:page>')
@login_required
def index(page):
    conn = mysql.get_db()
    db = conn.cursor()
    offset = 0
    lsts = []

    if page > 0:
        offset = (page * 15)

    db.execute("""SELECT * FROM lists
                  ORDER BY date_added
                  DESC LIMIT 15 OFFSET %s""" % offset)
    cols = tuple([d[0].decode('utf8') for d in db.description])
    _lists = [dict(zip(cols, row)) for row in db]
    for lst in _lists:
        lid = lst['lists_id']
        db.execute('SELECT COUNT(list_id) \
                    FROM recipients WHERE list_id = %s' % lid)
        recip_count = db.fetchall()
        if recip_count > 0:
            lst['recip_count'] = recip_count[0][0]
        else:
            lst['recip_count'] = 0
        lst['date_added'] = unix_to_local(lst['date_added'])
        lsts.append(lst)
    return render_template('subscribers/index.html', lists=lsts, page=page)


@mod.route('/create_list', methods=['GET', 'POST'])
@login_required
def create_list():
    error = None
    conn = mysql.get_db()
    db = conn.cursor()

    if request.method == 'POST':
        errors = [opt for opt, val in request.form.iteritems()
                  if (val not in ('first_name', 'last_name', 'email')
                      and val == '')]
        if len(errors) > 0:
            error = [error_dict.get(err) for err in errors
                     if error_dict.get(err) != '']
        else:
            try:
                db.execute("""INSERT into lists
                            (
                                name,
                                description,
                                date_added
                            )

                            VALUES (
                                %s, #name
                                %s, #description
                                %s) #date_added
                            """,
                           (
                           request.form['name'],
                           request.form['description'],
                           int(time.time())
                           )
                           )
                conn.commit()
            except Exception, e:
                conn.rollback()
                error = e
                return render_template('subscribers/details.html', error=error,
                                       editing=False)
            return redirect(url_for('subscribers.index'))
    return render_template('subscribers/details.html', error=error,
                           editing=False)


@mod.route('/edit_list/<int:lid>', methods=['GET'])
@login_required
def edit_list(lid):
    _lid = lid
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT * FROM lists WHERE lists_id = %d' % lid)
    res = db.fetchone()
    if res:
        cols = tuple([d[0].decode('utf8') for d in db.description])
        lst = dict(zip(cols, res))
        db.execute('SELECT first_name, last_name, email FROM `recipients` \
                    WHERE list_id = %d' % lid)
        recips = db.fetchall()
        recips = ['%s %s %s' % recip for recip in recips]
        recips = [r.encode('ascii', 'ignore') for r in recips]
        if len(recips) < 1:
            recips = ['No recipients']
        if request.method == 'GET':
            edit_name = request.args.get('recip_name')
            edit_email = request.args.get('recip_email')
            print 'ok'
            return render_template('subscribers/details.html', editing=True,
                                   list=lst, recipients=recips, list_id=_lid,
                                   edit_name=edit_name, edit_email=edit_email)
        return render_template('subscribers/details.html', editing=True,
                               list=lst, recipients=recips, list_id=_lid)
    #abort 404


@mod.route('/edit_recipients', methods=['GET', 'POST'])
@login_required
def edit_recipients():
    action = None
    conn = mysql.get_db()
    db = conn.cursor()
    if request.method == 'POST':
        email = request.form['recipChoice'].encode('ascii', 'ignore')
        if 'delete' in request.form.keys():
            action = 'delete'
        elif 'edit' in request.form.keys():
            action = 'edit'
        elif 'confirm_edit' in request.form.keys():
            action = 'confirm_edit'
        else:
            action = 'add'

        lid = request.form['list_id'].encode('ascii', 'ignore')

        if action == 'delete':
            try:
                db.execute('DELETE FROM recipients WHERE list_id = %s \
                            AND email = "%s"' % (lid, email))
                conn.commit()
            except Exception, e:
                print e
                conn.rollback()

    if action == 'add':
        first_name = request.form['new_name'].split()[0]
        last_name = request.form['new_name'].split()[1]
        email = request.form['new_email']
        try:
            db.execute("""INSERT INTO recipients
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
            print e
            conn.rollback()
            return redirect(url_for('subscribers.index'))
        return redirect(url_for('subscribers.edit_list', lid=lid))
    if action == 'confirm_edit':
        #iterate error_dict to check for missing items
        new_name = request.form['new_name']
        if len(new_name.split()) < 2:
            return redirect(url_for('subscribers.index'))
        first_name = request.form['new_name'].split()[0]
        last_name = request.form['new_name'].split()[1]
        new_email = request.form['new_email']
        old_email = request.form['old_email']
        try:
            db.execute("""UPDATE recipients
                       SET first_name=%s, last_name=%s, email=%s
                       WHERE email=%s AND lid = %s""",
                       (first_name, last_name, new_email, old_email, lid))
            conn.commit()
        except Exception, e:
            print e
            conn.rollback()
            return redirect(url_for('subscribers.index'))
    elif action == 'edit':
        recip_info = request.form['recipChoice'].split(',')
        recip_name = recip_info[0][1:]
        recip_email = recip_info[1][1:len(recip_info[1]) - 1]
        return redirect(url_for('subscribers.edit_list', lid=lid,
                        recip_name=recip_name, recip_email=recip_email))
    return redirect(url_for('subscribers.index'))


@mod.route('/delete_list/<int:lid>')
@login_required
def delete_campaign(lid):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('DELETE FROM lists WHERE lists_id = %d' % lid)
    conn.commit()
    return redirect(url_for('subscribers.index'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@mod.route('/upload_csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    conn = mysql.get_db()
    db = conn.cursor()
    if request.method == 'POST':
        lid = request.form['list_id']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print os.path
            print os.path.join(UPLOAD_FOLDER, filename)
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
                        db.execute("""INSERT INTO recipients
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
                        print e
                        conn.rollback()
                        return redirect(url_for('subscribers.index'))
    return redirect(url_for('subscribers.index'))
