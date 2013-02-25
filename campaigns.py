import os, sys
from flask import Blueprint, request, redirect, url_for, abort, \
     render_template, _app_ctx_stack
from flaskext.mysql import MySQL
#import settings
error_dict = {'code':'Please enter a campaign code', 
            'replyto_email':'Please enter a reply-to email', 
            'from_email':'Please enter a from email',
             'from_name':'Please enter a from name', 
             'companies_id':'Please enter a company', 
             'subject':'Please enter a subject', 
             'from_name_sel':'','replyto_sel':'','from_email_sel':''
             }

mod = Blueprint('campaigns', __name__)

@mod.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    error = None
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT companies_id, name FROM `companies`')
    companies = db.fetchall()
    db.execute('SELECT name, email FROM `staff`')
    staff = db.fetchall()

    if request.method == 'POST':
        errors = [opt for opt, val in request.form.iteritems() if val == '']
        if len(errors) > 1:
            error = [error_dict.get(err) for err in errors 
                        if error_dict.get(err) != '']
        else:
            try:
                db.execute("""INSERT INTO newsletters 
                            (name, author, code, date_sent, priority) 
                            VALUES (%s, %s, %s, %s, %s)""",
                            (request.form['subject'], 'John Doe', 
                            request.form['code'], 5, 3)
                            )
                conn.commit()
            except Exception as e:
                print e
                conn.rollback()
            return redirect(url_for('index'))

    return render_template('create_campaign.html', companies=companies, 
                                staff=staff, error=error)

@mod.route('/edit_campaign/<int:nid>')
def edit_campaign(nid):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT * FROM `newsletter` WHERE id = %d' % nid)
    res = db.fetchone()
    if res:
        cols = tuple([d[0].decode('utf8') for d in db.description])
        newsletter = dict(zip(cols, res))
        db.execute("""SELECT companies_title 
                        FROM companies 
                        WHERE companies_id = %d""" 
                        % newsletter['companies_id'])
        newsletter['companies_id'] = db.fetchall()[0][0]
        db.execute('SELECT companies_id, companies_title FROM `companies`')
        companies = db.fetchall()
        db.execute('SELECT name, email FROM `staff`')
        staff = db.fetchall()
        return render_template("edit_campaign.html", newsletter=newsletter, 
                                    staff=staff, companies=companies)
    abort(404)

@mod.route('/delete_campaign/<int:nid>')
def delete_campaign(nid):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('DELETE FROM newsletter WHERE id = %d' % nid)
    return redirect(url_for('index'))

@mod.route('/search/', methods=['POST'])
def search():
    query = request.form['query']