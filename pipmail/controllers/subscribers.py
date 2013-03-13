from flask import Blueprint, request, abort, render_template, redirect, url_for
from flaskext.mysql import MySQL
from pipmail.auth import login_required
import time
import datetime

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
def lists(page):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT COUNT(lists_id) FROM lists')
    count = db.fetchall()
    print count
    db.execute("""SELECT * FROM `lists`
                ORDER BY date_added DESC LIMIT 15 OFFSET %s""" % page)
    cols = tuple([d[0].decode('utf8') for d in db.description])
    _lists = [dict(zip(cols, row)) for row in db]
    lists = []
    for lst in _lists:
        unix_to_local = int(lst['date_added'])
        lst['date_added'] = datetime.datetime.fromtimestamp(
            unix_to_local).strftime('%Y-%m-%d %I:%M:%S')
        lists.append(lst)
    return render_template('subscribers/lists.html', lists=lists, page=page)


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
            return redirect(url_for('subscribers.lists'))
    return render_template('subscribers/details.html', error=error,
                           editing=False)


@mod.route('/edit_list/<int:lid>')
@login_required
def edit_list(lid):

    if request.method == 'POST':
        pass
    return render_template('subscribers/details.html', editing=True)
    abort(404)
