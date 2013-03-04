import time
from flask import Blueprint, request, redirect, url_for, abort, \
    render_template, current_app
from flask.ext.mysql import MySQL


error_dict = {'code': 'Please enter a campaign code',
              'replyto_email': 'Please enter a reply-to email',
              'from_email': 'Please enter a from email',
              'from_name': 'Please enter a from name',
              'company': 'Please enter a company',
              'subject': 'Please enter a subject',
              }


mysql = MySQL()
mod = Blueprint('campaigns', __name__)


@mod.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    app = current_app._get_current_object()
    if not authorize(app):
        return render_template('auth/login.html')

    error = None
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT companies_id, name FROM `companies`')
    companies = db.fetchall()
    db.execute('SELECT name, email FROM `staff`')
    staff = db.fetchall()

    if request.method == 'POST':

        errors = [opt for opt, val in request.form.iteritems()
                  if (val == '' and opt[:len(opt) - 3] != 'sel')]

        if len(errors) > 1:
            error = [error_dict.get(err) for err in errors
                     if error_dict.get(err) != '']
        else:
            print request.form
            for k, v in request.form.iteritems():
                print k, v
            try:
                db.execute("""INSERT INTO newsletters
                            (
                                code,
                                name,
                                author,
                                company,
                                from_name,
                                from_email,
                                replyto_email,
                                date_added,
                                date_sent,
                                priority,
                                unsub
                            )

                            VALUES (
                                %s, #code
                                %s, #name
                                %s, #author
                                %s, #company
                                %s, #from_name
                                %s, #from_email
                                %s, #replyto_email
                                %s, #date_added
                                %s, #date_sent
                                %s, #priority
                                %s) #unsub
                            """,
                          (
                           request.form['code'],
                           request.form['subject'],
                           'Me',
                           request.form['company'],
                           request.form['from_name'],
                           request.form['from_email'],
                           request.form['replyto_email'],
                           int(time.time()),
                           0,  # date sent
                           request.form['priority'],
                           request.form['unsub']  # unsub
                           )
                           )
                conn.commit()
            except Exception, e:
                print e
                conn.rollback()
            return redirect(url_for('index'))

    return render_template('campaigns/details.html', companies=companies,
                           staff=staff, error=error, editing=False)


@mod.route('/edit_campaign/<int:nid>')
def edit_campaign(nid):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('SELECT * FROM `newsletters` WHERE newsletters_id = %d' % nid)
    res = db.fetchone()
    if res:
        cols = tuple([d[0].decode('utf8') for d in db.description])
        newsletter = dict(zip(cols, res))
        db.execute("""SELECT name
                        FROM companies
                        WHERE companies_id = %d"""
                   % newsletter['company'])

        try:
            newsletter['company'] = db.fetchall()[0][0]
        except:
            newsletter['company'] = 'None'
        db.execute('SELECT companies_id, name FROM `companies`')
        companies = db.fetchall()
        db.execute('SELECT name, email FROM `staff`')
        staff = db.fetchall()
        return render_template("campaigns/details.html", newsletter=newsletter,
                               staff=staff, companies=companies, editing=True)
    abort(404)


@mod.route('/delete_campaign/<int:nid>')
def delete_campaign(nid):
    conn = mysql.get_db()
    db = conn.cursor()
    db.execute('DELETE FROM newsletters WHERE newsletters_id = %d' % nid)
    conn.commit()
    return redirect(url_for('index'))


# @mod.route('/search/', methods=['POST'])
# def search():
#     query = request.form['query']
