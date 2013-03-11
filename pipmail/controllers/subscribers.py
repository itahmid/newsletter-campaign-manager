from flask import Blueprint, request, abort, render_template
from flaskext.mysql import MySQL
from pipmail.auth import login_required


mysql = MySQL()
mod = Blueprint('subscribers', __name__)


@mod.route('/lists', defaults={'page': 1})
@mod.route('/lists/page/<int:page>')
@login_required
def lists(page):
    conn = mysql.get_db()
    db = conn.cursor()
    #db.execute('SELECT COUNT(id) FROM newsletter')
    #count = db.fetchall()
    db.execute("""SELECT * from `lists`
                ORDER BY date_created DESC LIMIT 15 OFFSET %s""" % page)
    cols = tuple([d[0].decode('utf8') for d in db.description])
    lists = [dict(zip(cols, row)) for row in db]
    # print lists
    # for l in lists:
    #     print l
    return render_template('subscribers/lists.html', lists=lists, page=page)


@mod.route('/create_list', methods=['GET', 'POST'])
@login_required
def create_list():
    error = None

    if request.method == 'POST':
        pass
    return render_template('subscribers/details.html', error=error,
                           editing=False)


@mod.route('/edit_list/<int:lid>')
@login_required
def edit_list(lid):

    if request.method == 'POST':
        pass
    return render_template('subscribers/details.html', editing=True)
    abort(404)
