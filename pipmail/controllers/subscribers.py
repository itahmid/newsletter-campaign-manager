from flask import Blueprint, request, abort, render_template, redirect, url_for
from flaskext.mysql import MySQL
from pipmail.helpers import login_required, unix_to_local
import time

error_dict = {'name': 'Please enter a name for this list',
              'description': 'Please enter a brief description for this list',
              'first_name': 'Please enter a first name for this recipient',
              'last_name': 'Please enter a last name for this recipient',
              'email': 'Please enter an email address for this recipient',
              }


mysql = MySQL()
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
            lst['list_count'] = recip_count
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
                  if (val == '')]
        if len(errors) > 1:
            error = [error_dict.get(err) for err in errors
                     if error_dict.get(err) != '']
        else:
            for k, v in request.form.iteritems():
                print k, v
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
                print e
                conn.rollback()
            #return render_template('subscribers/lists.html', success=True,
                                   #lists=lists, page=1)
            return redirect(url_for('subscribers.index'))
    return render_template('subscribers/details.html', error=error,
                           editing=False)


@mod.route('/edit_list/<int:lid>')
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
        db.execute('SELECT * FROM `recipients` WHERE list_id = %d' % lid)
        recips = db.fetchall()
        if len(recips) < 1:
            recips = ['No recipients']
        return render_template('subscribers/details.html', editing=True,
                               list=lst, recipients=recips, list_id=_lid)
    abort(404)


@mod.route('/edit_recipients', methods=['GET', 'POST'])
@login_required
def edit_recipients():
    conn = mysql.get_db()
    db = conn.cursor()
    if request.method == 'POST':
        first_name, last_name = request.form['new_name'].split()
        email = request.form['new_email']
        lid = request.form['list_id']
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


@mod.route('/delete_list/<int:lid>')
@login_required
def delete_campaign(lid):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('DELETE FROM lists WHERE lists_id = %d' % lid)
    conn.commit()
    return redirect(url_for('subscribers.index'))
