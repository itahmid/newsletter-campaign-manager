import os, sys, time
from flask import Blueprint, request, redirect, url_for, abort, \
     render_template, _app_ctx_stack
from flaskext.mysql import MySQL



error_dict = {'code':'Please enter a campaign code', 
            'replyto_email':'Please enter a reply-to email', 
            'from_email':'Please enter a from email',
             'from_name':'Please enter a from name', 
             'companies_id':'Please enter a company', 
             'subject':'Please enter a subject', 
             'from_name_sel':'','replyto_sel':'','from_email_sel':''
             }

mysql = MySQL()
mod = Blueprint('subscribers', __name__)

@mod.route('/lists', defaults={'page': 1})
@mod.route('/lists/page/<int:page>')
def lists(page):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT COUNT(id) FROM newsletter')
    count = db.fetchall()
    db.execute("""SELECT * from `newsletter_list` 
                ORDER BY CreatedOn DESC LIMIT 15 OFFSET %s""" % page)
    cols = tuple([d[0].decode('utf8') for d in db.description])
    lists = [dict(zip(cols, row)) for row in db]
    print lists
    for l in lists:
        print l
    return render_template('subscribers/lists.html', lists=lists, page=page)

@mod.route('/create_list', methods=['GET', 'POST'])
def create_list():
    error = None

    if request.method == 'POST':
        pass
    return render_template('subscribers/details.html', error=error)

@mod.route('/edit_list/<int:lid>')
def edit_list(lid):
    error = None
    
    if request.method == 'POST':
        pass
    return render_template('subscribers/details.html', error=error)
    abort(404)